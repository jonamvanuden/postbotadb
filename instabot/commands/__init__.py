# Import the classes from their specific files
from .snaptotopcommand import SnapToTopCommand, SnapToTopCommand2
from .clickbuttoncommand import ClickButtonCommand
from .watchcommand import WatchPostCommand
from .likewithdoubletapcommand import LikeWithDoubleTapCommand
from .commandstatus import CommandStatus
from .swipedowncommand import SwipeDownCommand, SwipeDrownFromBoxCommand
from .openconversationcommand import OpenConversationCommand
from .findandopenunreadcommand import FindAndOpenUnreadCommand
from .sendmessagecommand import SendMessageCommand
from .scrollcommand import ScrollCommand,ScrollToBottomCommand
from .systemcommands import OpenInstagramCommand, CloseInstagramCommand

# This list defines what gets imported when you use "from commands import *"
__all__ = [
    'SnapToTopCommand',
    'ClickButtonCommand',
    'SnapToTopCommand2',
    'CommandStatus',
    'WatchPostCommand',
    'LikeWithDoubleTapCommand',
    'SwipeDownCommand',
    'SwipeDrownFromBoxCommand',
    'OpenConversationCommand',
    'FindAndOpenUnreadCommand',
    'SendMessageCommand',
    'ScrollCommand',
    'ScrollToBottomCommand',
    'OpenInstagramCommand',
    'CloseInstagramCommand'
]