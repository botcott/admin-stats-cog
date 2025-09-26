from .admin_stats_cog import AdminStatsCog

def setup(bot):
    bot.add_cog(AdminStatsCog(bot))