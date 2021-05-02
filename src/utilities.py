import things
from PyInquirer import prompt
from rich.table import Table
from collections import Counter
from datetime import datetime


def askForTimeFrame():
    """
    Presents a list so the user can select the timeframe for results.

    Raises
    -------
        ValueError: If it breaks it will let the user know where it went wrong.

    Returns
    -------
        str: A string to pass into the things.py api that sets the timeframe
        for results.
    """

    questions = [
        {
            'type': 'list',
            'name': 'timeframe',
            'message': 'How far back do you want results?',
            'choices': [
                'Past Month',
                'Past Week',
                'Custom',
            ]
        },
        {
            'type': 'input',
            'name': 'daysBack',
            'message': 'How many days back would you like results for?:',
            'default': lambda x: '7',
            'validate': lambda val: int(val) > 0,
            'when': lambda answers: answers['timeframe'] == 'Custom'
        }
    ]
    answers = prompt(questions)

    if answers['timeframe'] == 'Past Month':
        timeFrame = "30d"
    elif answers['timeframe'] == 'Past Week':
        timeFrame = "7d"
    elif answers['timeframe'] == 'Custom':
        timeFrame = answers['daysBack'] + "d"
    else:
        raise ValueError(
            "Something went wrong when parsing days back"
        )

    return timeFrame


def printIncompleteTasks(tasksList, project, console):
    """
    Prints a table of incomplete tasks with information on project,
    date created, and the title of the todo. Project and todo title
    are hyperlinked to the location in the things app. The hyperlink
    can be accessed by holding cmd and clicking on the text.

    Params
    -------
        tasksList (list of dicts): A list of tasks where each task is a dicitonary
        project (str): User is given the option to filter the table to a specific
        project. The user choice is passed in and used to filter the results.
        console (Console): Rich text Console object for printing results
    """
    # Sort Tasks by Date
    sortedTable = sorted(
        tasksList, key=lambda e: e['created'], reverse=True)

    table = Table(title="Incomplete Tasks")
    table.add_column("Project", justify="center")
    table.add_column("Date Created", justify="center")
    table.add_column("Title", justify="left")

    for i in sortedTable:
        if project == "All":
            table = buildTaskTable(i, table)
        elif project == i['project_title']:
            table = buildTaskTable(i, table)

    print("\n")
    console.print(table)
    print("\n")


def buildTaskTable(task, table):
    """
    Used by 'printIncompleteTasks()' to build the table of incomplete tasks.

    Params
    -------
        task (dict): Dictionary containing info on a given task
        table (table): Table object generated by Rich

    Returns
    -------
        table: Returns a filled out table object for printing
    """
    url_todo = f"things:///show?id={task['uuid']}"
    url_project = f"things:///show?id={task['project']}"
    project_title = task['project_title']
    todo_title = task['title']

    table.add_row(f"[link={url_project}]{project_title}[/link]",
                  task['created'][0:10],
                  f"[link={url_todo}]{todo_title}[/link]"
                  )

    return table


def printTrends(console):
    """
    Prints rich table of trends by month sorted by year/month.

    Params
    -------
        console (Console): Console object created by Rich
    """
    allTasks = things.tasks(type='to-do', status=None, index='todayIndex')

    tasksCountsByMonth = collectTaskCountsByMonth(allTasks)
    table = Table(title="Monthly Task Completion Rate")
    table.add_column("Date", justify="center")
    table.add_column("Number Created", justify="center")
    table.add_column("Number Completed", justify="center")
    table.add_column("Percent Completed", justify="center")

    for i in tasksCountsByMonth:
        completionRate = round((i['CountCompleted']/i['Count']) * 100, 0)
        table.add_row(i['YearMonth'],
                      str(i['Count']),
                      str(i['CountCompleted']),
                      str(completionRate) + "%")

    print("\n")
    console.print(table)
    print("\n")


def collectTaskCountsByMonth(taskList):
    """
    Takes in a list of tasks and returns a sorted table counting the
    number of tasks created in each month and the number completed
    in each month.

    Params
    -------
        allTasks ([list of dicts]): A list of dictionaries where each
        dictionary is a task.

    Returns
    -------
        [list of dicts]: Returns a sorted list of dictionaries that
        has information on the # of tasks created by year-month and
        # completed.
    """

    yearMonth = [datetime.strptime(
        i['created'], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m') for i in taskList]

    yearMonthCompleted = [datetime.strptime(
        i['created'], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m') for i in taskList if i['status'] == 'completed']

    countDict = {}
    for i in yearMonth:
        if i not in countDict.keys():
            countDict[i] = yearMonth.count(i)

    completedCountDict = {}
    for i in yearMonthCompleted:
        if i not in completedCountDict.keys():
            completedCountDict[i] = yearMonthCompleted.count(i)

    combinedCountsListDict = []
    for i, val in enumerate(countDict):
        combinedCountsListDict.append({'YearMonth': val, 'Count': countDict[val],
                                       'CountCompleted': completedCountDict[val],
                                       'Year': int(val[0:4]), 'Month': int(val[5:7])})

    sortedTable = sorted(
        combinedCountsListDict, key=lambda x: (x['Year'], x['Month']), reverse=True)

    for i in sortedTable:
        del i['Year']
        del i['Month']

    return sortedTable


def getIncompleteByProject(console):
    """
    Collects number of incomplete todos by project title and prints the table

    Params:
    -------
        console (Console): Console object supplied by Rich
    """

    allTasks = things.todos(status=None)

    # Total Todos per project
    allProjectTitles = [i['project_title']
                        if 'project_title' in i else 'No Project' for i in allTasks]
    totalToDosPerProject = Counter(allProjectTitles)

    # Completed Todos per project
    completedProjectTitles = []
    for i in allTasks:
        if i['status'] == 'completed' and 'project_title' in i:
            completedProjectTitles.append(i['project_title'])
        elif i['status'] == 'completed' and 'project_title' not in i:
            completedProjectTitles.append('No Project')
    completedToDosPerProject = Counter(completedProjectTitles)

    # Combining Counts
    combinedCounts = {}
    for i in totalToDosPerProject:
        if i in completedToDosPerProject:
            combinedCounts[i] = [
                totalToDosPerProject[i],
                completedToDosPerProject[i],
                totalToDosPerProject[i] - completedToDosPerProject[i]
            ]
        else:
            combinedCounts[i] = [totalToDosPerProject[i], 0, 0]

    # Calculating Order by num not completed
    ordered = sorted(combinedCounts.items(),
                     key=lambda val: val[1][2], reverse=True)

    # Creating table for printing

    table = Table(title="Tasks by Project")
    table.add_column("Project", justify="left")
    table.add_column("# Todos", justify="center")
    table.add_column("# Incomplete", justify="center")

    for i in ordered:
        table.add_row(i[0],
                      str(i[1][0]),
                      str(i[1][2]))

    print("\n")
    console.print(table)
    print("\n")
