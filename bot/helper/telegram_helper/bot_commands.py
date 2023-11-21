from bot import CMD_SUFFIX


class _BotCommands:
    def __init__(self):
        self.StartCommand = f"start{CMD_SUFFIX}"
        self.MirrorCommand = [f"pea{CMD_SUFFIX}", f"p{CMD_SUFFIX}"]
        self.QbMirrorCommand = [f"peaqb{CMD_SUFFIX}", f"pqb{CMD_SUFFIX}"]
        self.YtdlCommand = [
            f"ytdl{CMD_SUFFIX}", f"peay{CMD_SUFFIX}", f"peawatch{CMD_SUFFIX}", f"pw{CMD_SUFFIX}"]
        self.LeechCommand = [f"pealeech{CMD_SUFFIX}", f"pl{CMD_SUFFIX}"]
        self.QbLeechCommand = [f"peaqbleech{CMD_SUFFIX}", f"pqbl{CMD_SUFFIX}"]
        self.YtdlLeechCommand = [
            f"ytdlleech{CMD_SUFFIX}", f"peaytdl{CMD_SUFFIX}", f"peawatchleech{CMD_SUFFIX}", f"pwl{CMD_SUFFIX}"]
        self.CloneCommand = [f"peaclone{CMD_SUFFIX}", f"pcl{CMD_SUFFIX}"]
        self.CountCommand = [f"peacount{CMD_SUFFIX}", f"pco{CMD_SUFFIX}"]
        self.DeleteCommand = [f"peadelete{CMD_SUFFIX}", f"pdel{CMD_SUFFIX}"]
        self.CancelTaskCommand = [f"peac{CMD_SUFFIX}", f"pc{CMD_SUFFIX}"]
        self.CancelAllCommand = [f"peacancelall{CMD_SUFFIX}", f"pca{CMD_SUFFIX}"]
        self.ListCommand = [f"pealist{CMD_SUFFIX}", f"pli{CMD_SUFFIX}"]
        self.SearchCommand = [f"peasearch{CMD_SUFFIX}", f"pse{CMD_SUFFIX}"]
        self.StatusCommand = [f"peastatus{CMD_SUFFIX}", f"psta{CMD_SUFFIX}"]
        self.UsersCommand = [f"peausers{CMD_SUFFIX}", f"pus{CMD_SUFFIX}"]
        self.AuthorizeCommand = [f"peaauthorize{CMD_SUFFIX}", f"pau{CMD_SUFFIX}"]
        self.UnAuthorizeCommand = [
            f"unauthorize{CMD_SUFFIX}", f"peaua{CMD_SUFFIX}"]
        self.AddSudoCommand = [f"peaaddsudo{CMD_SUFFIX}", f"as{CMD_SUFFIX}"]
        self.RmSudoCommand = [f"pearmsudo{CMD_SUFFIX}", f"rs{CMD_SUFFIX}"]
        self.PingCommand = [f"peaping{CMD_SUFFIX}", f"p{CMD_SUFFIX}"]
        self.RestartCommand = [f"pearestart{CMD_SUFFIX}", f"r{CMD_SUFFIX}"]
        self.StatsCommand = [f"peastats{CMD_SUFFIX}", f"sts{CMD_SUFFIX}"]
        self.HelpCommand = [f"peahelp{CMD_SUFFIX}", f"ph{CMD_SUFFIX}"]
        self.LogCommand = [f"pealog{CMD_SUFFIX}", f"lo{CMD_SUFFIX}"]
        self.ShellCommand = [f"peashell{CMD_SUFFIX}", f"sh{CMD_SUFFIX}"]
        self.SpeedCommand = [f"peaspeedtest{CMD_SUFFIX}", f"sp{CMD_SUFFIX}"]
        self.EvalCommand = [f"peaeval{CMD_SUFFIX}", f"ev{CMD_SUFFIX}"]
        self.ExecCommand = [f"peaexec{CMD_SUFFIX}", f"ex{CMD_SUFFIX}"]
        self.ClearLocalsCommand = [f"peaclearlocals{CMD_SUFFIX}", f"clo{CMD_SUFFIX}"]
        self.BotSetCommand = [f"peabsetting{CMD_SUFFIX}", f"bset{CMD_SUFFIX}"]
        self.UserSetCommand = [f"peausetting{CMD_SUFFIX}", f"uset{CMD_SUFFIX}"]
        self.BtSelectCommand = [f"peabtsel{CMD_SUFFIX}", f"bts{CMD_SUFFIX}"]
        self.RssCommand = f"pearss{CMD_SUFFIX}"


BotCommands = _BotCommands()
