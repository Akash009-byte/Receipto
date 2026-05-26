import logging
from ai_agents.image_downloader import ImageDownloader
from ai_agents.receipt_processor import ReceiptProcessor
from sqlalchemy.ext.asyncio import AsyncSession
from core.postgres import AsyncSessionLocal
from .commands import DiscordCommandHandler
from sheets_integration.sheets_service import SheetsService
from services.spreadsheet_service import SpreadsheetService
from services.worksheet_service import WorksheetService

logger = logging.getLogger(__name__)

class MessageEvents:
    """Handle all message-related Discord events."""
    
    def __init__(self, bot):
        self.bot = bot
        self.image_downloader = ImageDownloader(download_folder="dump")
        self.receipt_processor = ReceiptProcessor()
        self.register_events()
    
    def register_events(self):
        """Register all message events with the Discord bot."""
        
        @self.bot.event
        async def on_message(message):
            """Fired when a message is sent in a channel that the bot can access."""
            await self.handle_message(message)
        
        @self.bot.event
        async def on_message_edit(before, after):
            """Raised when a message is edited in a channel."""
            await self.handle_message_edit(before, after)
        
        @self.bot.event
        async def on_message_delete(message):
            """Called when a message is deleted in a channel."""
            await self.handle_message_delete(message)
    
    async def handle_message(self, message):
        """Handle incoming messages."""
        # Don't respond to our own messages
        if message.author == self.bot.user:
            return
        
        # Basic message info
        logger.info(f"Message received in #{message.channel.name}: '{message.content}' from {message.author.name}")

        # Parse and handle simple text commands (ss, ws)
        try:
            parsed = DiscordCommandHandler.parse_command(message.content)
            if parsed:
                cmd, arg = parsed
                async with AsyncSessionLocal() as session:
                    handler = DiscordCommandHandler(db_session=session)
                    if cmd == "ss":
                        reply = await handler.handle_ss(arg)
                    elif cmd == "ws":
                        reply = await handler.handle_ws(arg)
                    else:
                        reply = "⚠️ Unknown command."
                await message.channel.send(reply)
                return
        except Exception as e:
            logger.error(f"Error handling command: {e}")
            await message.channel.send("❌ Error handling command. Please try again.")
            return
        
        # Check for attachments (images, files, etc.)
        if message.attachments:
            logger.info(f"{len(message.attachments)} attachment(s) found:")
            for i, attachment in enumerate(message.attachments, 1):
                file_size_mb = attachment.size / (1024 * 1024)  # Convert to MB
                logger.info(f"  {i}. {attachment.filename} ({file_size_mb:.2f} MB)")
                logger.info(f"     URL: {attachment.url}")
                
                # Check if it's an image
                if any(attachment.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']):
                    logger.info(f"     🖼️ Image detected: {attachment.width}x{attachment.height}")
                    await self.handle_image_attachment(message, attachment)
                else:
                    logger.info(f"     📁 File attachment detected")
        
        # Check for embeds (rich content like YouTube links, etc.)
        if message.embeds:
            logger.info(f"🔗 {len(message.embeds)} embed(s) found:")
            for i, embed in enumerate(message.embeds, 1):
                logger.info(f"  {i}. Title: {embed.title or 'No title'}")
                logger.info(f"     URL: {embed.url or 'No URL'}")
                if embed.image:
                    logger.info(f"🖼️   Embedded image: {embed.image.url}")
      
    async def handle_message_edit(self, before, after):
        """Handle message edits."""
        # Don't log our own message edits
        if before.author == self.bot.user:
            return
        
        logger.info(f"Message edited in #{before.channel.name} by {before.author.name}")
        logger.info(f"  Before: '{before.content}'")
        logger.info(f"  After:  '{after.content}'")
    
    async def handle_message_delete(self, message):
        """Handle message deletions."""
        # Don't log our own message deletions
        if message.author == self.bot.user:
            return
        
        logger.info(f"Message deleted in #{message.channel.name} by {message.author.name}: '{message.content}'") 

    async def handle_image_attachment(self, message, attachment):
        """Handle image attachments specifically - download and process with AI."""
        try:
            logger.info(f"🖼️   Processing image: {attachment.filename}")
            
            # Step 1: Download the image
            file_path = await self.image_downloader.download_discord_attachment(
                attachment, message.author.name
            )
            
            if not file_path:
                await message.channel.send(f"❌ Failed to download image: {attachment.filename}")
                return
            
            # Step 2: Process with AI (Receipt Processing)
            await message.channel.send(f"🤖 Processing receipt with AI... Please wait!")
            
            receipt_data = await self.receipt_processor.process_receipt_image(file_path)
            
            # Step 3: Send results back to Discord
            if "error" in receipt_data:
                await message.channel.send(f"❌ AI Processing failed: {receipt_data['error']}")
            else:
                await self.send_receipt_results(message, receipt_data, attachment.filename)

                # Step 5: Write receipt to active spreadsheet/worksheet and update end_row
                try:
                    async with AsyncSessionLocal() as session:
                        ss_service = SpreadsheetService(session=session)
                        ws_service = WorksheetService(session=session)
                        sheets_service = SheetsService()

                        active_spreadsheet = await ss_service.get_active_spreadsheet()
                        if not active_spreadsheet:
                            await message.channel.send("⚠️ No active spreadsheet set. Use 'ss <name>' to set one.")
                            return

                        active_worksheet = await ws_service.get_active_worksheet(active_spreadsheet.id)
                        if not active_worksheet:
                            await message.channel.send(f"⚠️ No active worksheet for spreadsheet '{active_spreadsheet.name}'. Use 'ws <name>' to create/activate one.")
                            return

                        start_row = active_worksheet.end_row or 1
                        write_result = await sheets_service.write_receipt_to_sheet(
                            spreadsheet_name=active_spreadsheet.name,
                            worksheet_name=active_worksheet.name,
                            start_row=start_row,
                            receipt_data=receipt_data
                        )

                        if write_result.get("status") == "success":
                            # Advance end_row by +5 after writing
                            new_end_row = int(write_result.get("data", {}).get("end_row", start_row)) + 5
                            await ws_service.update_worksheet(
                                worksheet_id=active_worksheet.id,
                                end_row=new_end_row
                            )
                            await message.channel.send(
                                f"✅ Receipt appended to '{active_spreadsheet.name}' → '{active_worksheet.name}'. Next start row: {new_end_row}."
                            )
                        else:
                            await message.channel.send(
                                f"❌ Failed to write receipt to sheet: {write_result.get('error', 'Unknown error')}"
                            )
                except Exception as e:
                    logger.error(f"Error writing receipt to sheet: {e}")
                    await message.channel.send("❌ Error writing receipt to Google Sheets.")
            
            # Step 4: Cleanup if needed
            file_count = self.image_downloader.get_downloaded_files_count()
            if file_count > 50:  # Cleanup when we have too many files
                self.image_downloader.cleanup_old_files(max_files=30)
                
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            await message.channel.send(f"❌ Error processing image: {str(e)}")
    
    async def send_receipt_results(self, message, receipt_data, filename):
        """Send formatted receipt results to Discord."""
        try:
            # Format the receipt data nicely
            vendor = receipt_data.get('vendor', 'Unknown')
            date = receipt_data.get('date', 'Unknown')
            total = receipt_data.get('total', 0.0)
            items_count = len(receipt_data.get('items', []))
            
            # Create a nice summary
            summary = f"""
🧾 **Receipt Processed Successfully!**

📋 **Details:**
• **Vendor:** {vendor}
• **Date:** {date}
• **Total:** ${total}
• **Items:** {items_count} item(s)
• **File:** {filename}

✅ **Status:** {'Valid' if receipt_data.get('validation_passed', False) else 'Needs Review'}
            """.strip()
            
            await message.channel.send(summary)
            
            # If there are items, show them too
            if receipt_data.get('items') and len(receipt_data['items']) > 0:
                items_text = "📝 **Items:**\n"
                for i, item in enumerate(receipt_data['items'], 1):  # Show ALL items
                    name = item.get('name', 'Unknown item')
                    price = item.get('price', 0.0)
                    items_text += f"{i}. {name} - ${price}\n"
                
                await message.channel.send(items_text)
            
            logger.info(f"✅ Successfully processed receipt for {message.author.name}")
            
        except Exception as e:
            logger.error(f"Error sending receipt results: {e}")
            await message.channel.send(f"✅ Receipt processed, but error formatting results: {str(e)}") 