#!/usr/bin/env python
"""Susu Telegram Bot - Savings Goal Tracker with USDC wallet monitoring."""
import asyncio
import logging
from datetime import datetime

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from config import get_config
from storage import get_goals, save_goals, get_deposits, save_deposits, get_wallet_state, save_wallet_state
from wallet import get_usdc_balance

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# --- Goal Commands ---

async def cmd_goal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add a goal: /goal <name> <amount>"""
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /goal <name> <amount>")
        return
    
    name = context.args[0]
    try:
        amount = float(context.args[1])
    except ValueError:
        await update.message.reply_text("Amount must be a number.")
        return
    
    goals = get_goals()
    goals[name] = {"target": amount, "saved": 0.0}
    save_goals(goals)
    await update.message.reply_text(f"✅ Goal '{name}' added: ${amount:.2f}")


async def cmd_goals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all goals: /goals"""
    goals = get_goals()
    if not goals:
        await update.message.reply_text("No goals yet. Add one with /goal <name> <amount>")
        return
    
    lines = ["📊 *Goals* (sorted by price):\n"]
    for name, data in sorted(goals.items(), key=lambda x: x[1]["target"]):
        target = data["target"]
        saved = data["saved"]
        pct = (saved / target * 100) if target > 0 else 0
        bar_len = 10
        filled = int(bar_len * pct / 100)
        bar = "█" * filled + "░" * (bar_len - filled)
        lines.append(f"*{name}*\n{bar} {pct:.0f}%\n${saved:.2f} / ${target:.2f}\n")
    
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


async def cmd_remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove a goal: /remove <name>"""
    if not context.args:
        await update.message.reply_text("Usage: /remove <name>")
        return
    
    name = context.args[0]
    goals = get_goals()
    if name in goals:
        del goals[name]
        save_goals(goals)
        await update.message.reply_text(f"🗑️ Goal '{name}' removed.")
    else:
        await update.message.reply_text(f"Goal '{name}' not found.")


async def cmd_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show wallet USDC balance: /balance"""
    try:
        balance = get_usdc_balance()
        await update.message.reply_text(f"💰 Wallet balance: ${balance:.2f} USDC")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Error fetching balance: {e}")


# --- Auto Sync ---

async def sync_wallet(app: Application):
    """Check wallet balance and create deposit if increased."""
    config = get_config()
    chat_id = config["telegram_chat_id"]
    
    try:
        current_balance = get_usdc_balance()
        wallet_state = get_wallet_state()
        last_balance = wallet_state.get("last_balance", 0.0)
        
        if current_balance > last_balance:
            deposit_amount = current_balance - last_balance
            
            # Process deposit to goals
            goals = get_goals()
            deposits = get_deposits()
            remaining = deposit_amount
            record = {"amount": deposit_amount, "date": datetime.now().isoformat(), "allocations": []}
            
            msg_lines = [f"💵 New deposit: ${deposit_amount:.2f} USDC\n"]
            
            while remaining > 0 and goals:
                top = min(goals.items(), key=lambda x: x[1]["target"])
                name, data = top
                needed = data["target"] - data["saved"]
                
                if remaining >= needed:
                    record["allocations"].append({"goal": name, "amount": needed})
                    del goals[name]
                    remaining -= needed
                    msg_lines.append(f"🎉 '{name}' complete!")
                else:
                    goals[name]["saved"] += remaining
                    record["allocations"].append({"goal": name, "amount": remaining})
                    msg_lines.append(f"→ ${remaining:.2f} to '{name}' ({goals[name]['saved']:.2f}/{data['target']:.2f})")
                    remaining = 0
            
            deposits.append(record)
            save_deposits(deposits)
            save_goals(goals)
            
            await app.bot.send_message(chat_id=chat_id, text="\n".join(msg_lines))
        
        # Update last known balance
        wallet_state["last_balance"] = current_balance
        save_wallet_state(wallet_state)
        
    except Exception as e:
        logger.error(f"Sync error: {e}")


async def periodic_sync(app: Application):
    """Run wallet sync every hour."""
    while True:
        await sync_wallet(app)
        await asyncio.sleep(3600)  # 1 hour


def main():
    config = get_config()
    app = Application.builder().token(config["telegram_bot_token"]).build()
    
    # Commands
    app.add_handler(CommandHandler("goal", cmd_goal))
    app.add_handler(CommandHandler("goals", cmd_goals))
    app.add_handler(CommandHandler("remove", cmd_remove))
    app.add_handler(CommandHandler("balance", cmd_balance))
    
    # Start periodic sync in background
    async def post_init(app: Application):
        asyncio.create_task(periodic_sync(app))
    
    app.post_init = post_init
    
    logger.info("🚀 Susu bot starting...")
    app.run_polling()


if __name__ == "__main__":
    main()
