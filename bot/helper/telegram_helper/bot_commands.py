from bot import CMD_SUFFIX


class _BotCommands:
    def __init__(self):
        self.StartCommand = f'start{CMD_SUFFIX}'
        self.MirrorCommand = [f'yg{CMD_SUFFIX}', f'm{CMD_SUFFIX}']
        self.QbMirrorCommand = [f'ygqb{CMD_SUFFIX}', f'qb{CMD_SUFFIX}']
        self.YtdlCommand = [
            f'ytdl{CMD_SUFFIX}', f'y{CMD_SUFFIX}', f'watch{CMD_SUFFIX}', f'w{CMD_SUFFIX}']
        self.LeechCommand = [f'ygleech{CMD_SUFFIX}', f'l{CMD_SUFFIX}']
        self.QbLeechCommand = [f'ygqbleech{CMD_SUFFIX}', f'qbl{CMD_SUFFIX}']
        self.YtdlLeechCommand = [
            f'ytdlleech{CMD_SUFFIX}', f'yl{CMD_SUFFIX}', f'watchleech{CMD_SUFFIX}', f'wl{CMD_SUFFIX}']
        self.CloneCommand = [f'ygclone{CMD_SUFFIX}', f'cl{CMD_SUFFIX}']
        self.CountCommand = [f'ygcount{CMD_SUFFIX}', f'co{CMD_SUFFIX}']
        self.DeleteCommand = [f'ygdelete{CMD_SUFFIX}', f'del{CMD_SUFFIX}']
        self.CancelMirror = [f'ygcancel{CMD_SUFFIX}', f'c{CMD_SUFFIX}']
        self.CancelAllCommand = [f'ygcancelall{CMD_SUFFIX}', f'ca{CMD_SUFFIX}']
        self.ListCommand = [f'yglist{CMD_SUFFIX}', f'li{CMD_SUFFIX}']
        self.SearchCommand = [f'ygsearch{CMD_SUFFIX}', f'se{CMD_SUFFIX}']
        self.StatusCommand = [f'ygstatus{CMD_SUFFIX}', f'sta{CMD_SUFFIX}']
        self.UsersCommand = [f'ygusers{CMD_SUFFIX}', f'us{CMD_SUFFIX}']
        self.AuthorizeCommand = [f'ygauthorize{CMD_SUFFIX}', f'au{CMD_SUFFIX}']
        self.UnAuthorizeCommand = [
            f'unauthorize{CMD_SUFFIX}', f'ua{CMD_SUFFIX}']
        self.AddSudoCommand = [f'ygaddsudo{CMD_SUFFIX}', f'as{CMD_SUFFIX}']
        self.RmSudoCommand = [f'ygrmsudo{CMD_SUFFIX}', f'rs{CMD_SUFFIX}']
        self.PingCommand = [f'ygping{CMD_SUFFIX}', f'p{CMD_SUFFIX}']
        self.RestartCommand = [f'ygrestart{CMD_SUFFIX}', f'r{CMD_SUFFIX}']
        self.StatsCommand = [f'ygstats{CMD_SUFFIX}', f'sts{CMD_SUFFIX}']
        self.HelpCommand = [f'yghelp{CMD_SUFFIX}', f'h{CMD_SUFFIX}']
        self.LogCommand = [f'yglog{CMD_SUFFIX}', f'lo{CMD_SUFFIX}']
        self.ShellCommand = [f'ygshell{CMD_SUFFIX}', f'sh{CMD_SUFFIX}']
        self.EvalCommand = [f'ygeval{CMD_SUFFIX}', f'ev{CMD_SUFFIX}']
        self.ExecCommand = [f'ygexec{CMD_SUFFIX}', f'ex{CMD_SUFFIX}']
        self.ClearLocalsCommand = [f'ygclearlocals{CMD_SUFFIX}', f'clo{CMD_SUFFIX}']
        self.BotSetCommand = [f'ygbsetting{CMD_SUFFIX}', f'bset{CMD_SUFFIX}']
        self.UserSetCommand = [f'ygusetting{CMD_SUFFIX}', f'uset{CMD_SUFFIX}']
        self.BtSelectCommand = [f'ygbtsel{CMD_SUFFIX}', f'bts{CMD_SUFFIX}']
        self.RssCommand = f'ygrss{CMD_SUFFIX}'


BotCommands = _BotCommands()
