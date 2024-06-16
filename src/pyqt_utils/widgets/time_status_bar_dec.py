from decorator import decorator


@decorator
def changeStatusDec(
    fun,
    msg='',
    failureMsg='',
    # SKIP: false positive - decorator changes signature
    returnValue=True,  # noqa: FBT002
    *args,
    **kwargs,
):
    """
    Change status depending on return value from decorated function.

    None -> (skip decorator)
    False -> failureMsg
    _ -> msg.
    """
    val = fun(*args, **kwargs)
    if val is False:
        msg = failureMsg
    elif val is None:
        return val

    self = args[0]
    try:
        statusBar = self.statusBar()
    except AttributeError:
        statusBar = self.parent().statusBar()

    statusBar.showMessage(msg)
    if returnValue:
        return val
    return None
