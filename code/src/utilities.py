def parseInputs(inputsList):
    """Parses command line inputs. Currently that is just
    a string that indicates the time period to do the analysis.

    Args:
        inputsList (list): List of inputs given at the command
        line.

    Returns:
        string: string that is then used to decide what time
        frame to analyze the results over.
    """
    if inputsList[1] in ['month', 'week']:
        timeFrame = inputsList[1]
    else:
        print("Please provide a timeframe of 'month' or 'week'")
        exit()

    return timeFrame


def


def askPrintTasks(createdTasks):
    """Asks user if they would like to see the tasks they made
    in the past week. Will repeat until the user answers yes
    or no.

    Args:
        createdTasks (list): list of tuples containing information
        on the tasks that have been created in the past week or month.
    """
    printTasks = input(
        "Would you like to see the created tasks [y/N]?\n").lower()

    if printTasks == 'y':
        for i in createdTasks:
            print(i)
    elif printTasks == 'n':
        pass
    else:
        print("Please answer with: y or N")
        askPrintTasks(createdTasks)

    return
