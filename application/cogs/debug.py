import coc 
import discord
from discord.ext import commands
from application.constants.emoji import Emoji

class Debug(commands.Cog):
    """Cog for various events and debugging"""
    def __init__(self, bot):
        self.bot = bot
        self.error_logs = None
        self.commands_debug = None
        self.task = self.bot.loop.create_task(self.initialize())
        self.bot.coc.add_events(self.on_event_error)
    
    def cog_unload(self):
        self.task.cancel()
        self.bot.coc.remove_events(self.on_event_error)

    async def initialize(self):
        await self.bot.wait_until_ready()
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):

        if isinstance(error, commands.errors.CommandNotFound):
            await ctx.send("That command doesn't exist.")
        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.send('This command cannot be used in private messages.')
        elif isinstance(error, commands.errors.TooManyArguments):
            await ctx.send(error)
        elif isinstance(error, commands.DisabledCommand):
            await ctx.send('Sorry. This command is disabled and cannot be used.')
        elif isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send(f"Not enough arguments supplied.")
            await ctx.send_help(ctx.command)
        elif isinstance(error, commands.errors.BadArgument):
            await ctx.send(f"Bad arguments supplied.")
            await ctx.send_help(ctx.command)
        elif isinstance(error, commands.errors.NotOwner):
            await ctx.send(f"This command is only for Pc !!!!")
        elif isinstance(error, discord.errors.Forbidden):
            await ctx.send("I don't have enough permsissions to do that!")
        elif isinstance(error, commands.errors.MissingPermissions):
            await ctx.send("You don't have enough permissions to use this command!")
        elif isinstance(error, commands.errors.CommandOnCooldown):
            pass
        elif isinstance(error, commands.errors.MissingAnyRole):
            await ctx.send(f" Only Admin can use this command.")
        elif isinstance(error,commands.errors.MaxConcurrencyReached):
            await ctx.send(f" One instance of this command is running. You need to wait till it completes")
        else:
            await ctx.send(f" Else : {error}")
        await ctx.message.add_reaction(Emoji.GREEN_CROSS)

    async def on_event_error(self,ctx,error):
        ctx.send(error)

def setup(bot):
    bot.add_cog(Debug(bot))
