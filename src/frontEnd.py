import ThingsData as td
import utilities
from datetime import datetime
from pywebio.input import input, FLOAT
from pywebio.output import put_text


if __name__ == '__main__':

    # Get requested timeframe
    timeFrame = utilities.askForTimeFrame()

    # Get stats
    stats = td.statsReport(timeFrame)
    createdTasks = stats.getNewTasks()
    completedTasks = stats.getRecentCompletedTasks()
    monthlyCompletions = stats.getMonthlyCompletionRate()

    # Report to standard output
    print("""
        In the past %s days you have created %s tasks 
        of which you have completed %s.\n""" %
          (timeFrame, len(createdTasks), len(completedTasks)))

    # Ask if user would like to see all uncompleted tasks
    uncompletedTasks = [i for i in createdTasks if i not in completedTasks]
    utilities.askPrintTasks(uncompletedTasks)

    # Print trends in task completions
    utilities.askPrintTrends(monthlyCompletions)
