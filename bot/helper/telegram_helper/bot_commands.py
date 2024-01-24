from bot import CMD_SUFFIX


class _BotCommands:
    def __init__(self):
        self.StartCommand = f"start{CMD_SUFFIX}"
        self.MirrorCommand = [f"pea{CMD_SUFFIX}", f"peam{CMD_SUFFIX}"]
        self.QbMirrorCommand = [f"peaqb{CMD_SUFFIX}", f"peaqm{CMD_SUFFIX}"]
        self.JdMirrorCommand = [f"peajd{CMD_SUFFIX}", f"peajm{CMD_SUFFIX}"]
        self.YtdlCommand = [
            f"peaytdl{CMD_SUFFIX}", f"peay{CMD_SUFFIX}", f"peawatch{CMD_SUFFIX}", f"peaw{CMD_SUFFIX}"]
        self.LeechCommand = [f"pealeech{CMD_SUFFIX}", f"peal{CMD_SUFFIX}"]
        self.QbLeechCommand = [f"peaqbleech{CMD_SUFFIX}", f"peaql{CMD_SUFFIX}"]
        self.JdLeechCommand = [f"peajdleech{CMD_SUFFIX}", f"peajl{CMD_SUFFIX}"]
        self.YtdlLeechCommand = [
            f"ytdlleech{CMD_SUFFIX}", f"peayl{CMD_SUFFIX}", f"watchleech{CMD_SUFFIX}", f"peawl{CMD_SUFFIX}"]
        self.CloneCommand = [f"peaclone{CMD_SUFFIX}", f"peacl{CMD_SUFFIX}"]
        self.CountCommand = [f"peacount{CMD_SUFFIX}", f"peaco{CMD_SUFFIX}"]
        self.DeleteCommand = [f"peadelete{CMD_SUFFIX}", f"peadel{CMD_SUFFIX}"]
        self.CancelTaskCommand = [f"peacancel{CMD_SUFFIX}", f"peac{CMD_SUFFIX}"]
        self.CancelAllCommand = [f"peacancelall{CMD_SUFFIX}", f"peaca{CMD_SUFFIX}"]
        self.ForceStartCommand = [f"peaforcestart{CMD_SUFFIX}", f"peafs{CMD_SUFFIX}"]
        self.ListCommand = [f"pealist{CMD_SUFFIX}", f"peali{CMD_SUFFIX}"]
        self.SearchCommand = [f"peasearch{CMD_SUFFIX}", f"pease{CMD_SUFFIX}"]
        self.StatusCommand = [f"peastatus{CMD_SUFFIX}", f"peasta{CMD_SUFFIX}"]
        self.UsersCommand = [f"peausers{CMD_SUFFIX}", f"peaus{CMD_SUFFIX}"]
        self.AuthorizeCommand = [f"peaauthorize{CMD_SUFFIX}", f"peaau{CMD_SUFFIX}"]
        self.UnAuthorizeCommand = [
            f"unauthorize{CMD_SUFFIX}", f"peaua{CMD_SUFFIX}"]
        self.AddSudoCommand = [f"peaaddsudo{CMD_SUFFIX}", f"peaas{CMD_SUFFIX}"]
        self.RmSudoCommand = [f"pearmsudo{CMD_SUFFIX}", f"pears{CMD_SUFFIX}"]
        self.PingCommand = [f"peaping{CMD_SUFFIX}", f"peap{CMD_SUFFIX}"]
        self.RestartCommand = [f"pearestart{CMD_SUFFIX}", f"pear{CMD_SUFFIX}"]
        self.StatsCommand = [f"peastats{CMD_SUFFIX}", f"peasts{CMD_SUFFIX}"]
        self.HelpCommand = [f"peahelp{CMD_SUFFIX}", f"peah{CMD_SUFFIX}"]
        self.LogCommand = [f"pealog{CMD_SUFFIX}", f"pealo{CMD_SUFFIX}"]
        self.ShellCommand = [f"peashell{CMD_SUFFIX}", f"peash{CMD_SUFFIX}"]
        self.SpeedCommand = [f"peaspeedtest{CMD_SUFFIX}", f"peasp{CMD_SUFFIX}"]
        self.ExecCommand = [f"peaexec{CMD_SUFFIX}", f"peaex{CMD_SUFFIX}"]
        self.AExecCommand = [f"peaaexec{CMD_SUFFIX}", f"peaaex{CMD_SUFFIX}"]
        self.ClearLocalsCommand = [f"peaclearlocal{CMD_SUFFIX}", f"peaclo{CMD_SUFFIX}"]
        self.BotSetCommand = [f"peabsetting{CMD_SUFFIX}", f"peabset{CMD_SUFFIX}", f"peabs{CMD_SUFFIX}"]
        self.UserSetCommand = [f"peausetting{CMD_SUFFIX}", f"peauset{CMD_SUFFIX}", f"peaus{CMD_SUFFIX}"]
        self.BtSelectCommand = [f"peabtsel{CMD_SUFFIX}", f"peabts{CMD_SUFFIX}"]
        self.RssCommand = f"pearss{CMD_SUFFIX}"


BotCommands = _BotCommands()
