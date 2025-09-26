import logging
import datetime

import discord
from discord.ext import commands

async def check_embed_is_admin_only(embed, ckey):
    text_to_check = []

    if embed.description:
        text_to_check.append(embed.description)

    if not text_to_check:
        return False

    for text in text_to_check:
        lines = text.splitlines()
        for line in lines:
            lower_line = line.lower()
            if "admin only" in lower_line and ckey in lower_line:
                return False

    return True

async def check_embed(embed, ckey):
    if embed.title and ckey in embed.title.lower():
        return True
    if embed.description and ckey in embed.description.lower():
        return True
    for field in embed.fields:
        if field.name and ckey in field.name.lower():
            return True
        if field.value and ckey in field.value.lower():
            return True
    return False


class AdminStatsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)

    @commands.slash_command(name="ahelp_stats", description="Количество отвеченных ахелпов")
    async def ahelp_stats(self, ctx: discord.ApplicationContext, channel: discord.Option(discord.TextChannel, "Канал с ахелпами", required=True), ckey: discord.Option(str, requied=True, description="Сикей администратора")):

        now = datetime.datetime.now()
        first_day_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        all_ahelps_with_mention = 0
        ahelps_without_admin_only = 0
        ahelps_with_admin_only = 0

        async for message in channel.history(limit=None, after=first_day_of_month):
            for embed in message.embeds:
                if await check_embed(embed, ckey):
                        all_ahelps_with_mention += 1
                        break
                
        async for message in channel.history(limit=None, after=first_day_of_month):
            for embed in message.embeds:
                if await check_embed(embed, ckey):
                        if await check_embed_is_admin_only(embed, ckey):
                            ahelps_without_admin_only += 1
                            break

        async for message in channel.history(limit=None, after=first_day_of_month):
            for embed in message.embeds:
                if await check_embed(embed, ckey):
                        if not await check_embed_is_admin_only(embed, ckey):
                            ahelps_with_admin_only += 1
                            break

        self.logger.info(f"Найдено {all_ahelps_with_mention} сообщений с упоминанием '{ckey}' в этом месяце")
        self.logger.info(f"Найдено {ahelps_without_admin_only} сообщений без Admin Only с упоминанием '{ckey}' в этом месяце")
        self.logger.info(f"Найдено {ahelps_with_admin_only} сообщений с Admin Only и с упоминанием '{ckey}' в этом месяце")

        now = datetime.datetime.now()
        date = now.strftime("%m.%Y")

        answer = discord.Embed(title=f"{ctx.author.name} | {channel.name} | {date}", colour=0x41f096)

        answer.add_field(name="Общее количество", inline=False,
            value=f"Было найдено {all_ahelps_with_mention} ахелпов"
        )
        answer.add_field(name="Без Admin Only", inline=False,
            value=f"Было найдено {ahelps_without_admin_only} ахелпов"
        )
        answer.add_field(name="Admin Only", inline=False,
            value=f"Было найдено {ahelps_with_admin_only} ахелпов"
        )

        await ctx.respond(embed=answer, ephemeral=True)