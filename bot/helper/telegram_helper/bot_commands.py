from bot import CMD_SUFFIX


class _BotCommands:
    def __init__(self):
        self.StartCommand = f'start{CMD_SUFFIX}'
        self.MirrorCommand = [f'pea{CMD_SUFFIX}', f'm{CMD_SUFFIX}']
        self.QbMirrorCommand = [f'peaqb{CMD_SUFFIX}', f'qb{CMD_SUFFIX}']
        self.YtdlCommand = [
            f'ytdl{CMD_SUFFIX}', f'y{CMD_SUFFIX}', f'watch{CMD_SUFFIX}', f'w{CMD_SUFFIX}']
        self.LeechCommand = [f'pealeech{CMD_SUFFIX}', f'l{CMD_SUFFIX}']
        self.QbLeechCommand = [f'peaqbleech{CMD_SUFFIX}', f'qbl{CMD_SUFFIX}']
        self.YtdlLeechCommand = [
            f'ytdlleech{CMD_SUFFIX}', f'yl{CMD_SUFFIX}', f'watchleech{CMD_SUFFIX}', f'wl{CMD_SUFFIX}']
        self.CloneCommand = [f'peaclone{CMD_SUFFIX}', f'cl{CMD_SUFFIX}']
        self.CountCommand = [f'peacount{CMD_SUFFIX}', f'co{CMD_SUFFIX}']
        self.DeleteCommand = [f'peadelete{CMD_SUFFIX}', f'del{CMD_SUFFIX}']
        self.CancelMirror = [f'peacancel{CMD_SUFFIX}', f'c{CMD_SUFFIX}']
        self.CancelAllCommand = [f'peacancelall{CMD_SUFFIX}', f'ca{CMD_SUFFIX}']
        self.ListCommand = [f'pealist{CMD_SUFFIX}', f'li{CMD_SUFFIX}']
        self.SearchCommand = [f'peasearch{CMD_SUFFIX}', f'se{CMD_SUFFIX}']
        self.StatusCommand = [f'peastatus{CMD_SUFFIX}', f'sta{CMD_SUFFIX}']
        self.UsersCommand = [f'peausers{CMD_SUFFIX}', f'us{CMD_SUFFIX}']
        self.AuthorizeCommand = [f'peaauthorize{CMD_SUFFIX}', f'au{CMD_SUFFIX}']
        self.UnAuthorizeCommand = [
            f'unauthorize{CMD_SUFFIX}', f'ua{CMD_SUFFIX}']
        self.AddSudoCommand = [f'peaaddsudo{CMD_SUFFIX}', f'as{CMD_SUFFIX}']
        self.RmSudoCommand = [f'pearmsudo{CMD_SUFFIX}', f'rs{CMD_SUFFIX}']
        self.PingCommand = [f'peaping{CMD_SUFFIX}', f'p{CMD_SUFFIX}']
        self.RestartCommand = [f'pearestart{CMD_SUFFIX}', f'r{CMD_SUFFIX}']
        self.StatsCommand = [f'peastats{CMD_SUFFIX}', f'sts{CMD_SUFFIX}']
        self.HelpCommand = [f'peahelp{CMD_SUFFIX}', f'h{CMD_SUFFIX}']
        self.LogCommand = [f'pealog{CMD_SUFFIX}', f'lo{CMD_SUFFIX}']
        self.ShellCommand = [f'peashell{CMD_SUFFIX}', f'sh{CMD_SUFFIX}']
        self.EvalCommand = [f'peaeval{CMD_SUFFIX}', f'ev{CMD_SUFFIX}']
        self.ExecCommand = [f'peaexec{CMD_SUFFIX}', f'ex{CMD_SUFFIX}']
        self.ClearLocalsCommand = [f'peaclearlocals{CMD_SUFFIX}', f'clo{CMD_SUFFIX}']
        self.BotSetCommand = [f'peabsetting{CMD_SUFFIX}', f'bset{CMD_SUFFIX}']
        self.UserSetCommand = [f'peausetting{CMD_SUFFIX}', f'uset{CMD_SUFFIX}']
        self.BtSelectCommand = [f'peabtsel{CMD_SUFFIX}', f'bts{CMD_SUFFIX}']
        self.RssCommand = f'pearss{CMD_SUFFIX}'


BotCommands = _BotCommands()
