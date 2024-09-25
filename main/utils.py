# main/utils.py
# Contains utility functions that can be used across the project.

from django.utils import timezone


def get_warning_msg(report_due_date: timezone, report: str):
    if report_due_date is None:
        warning = False
        warning_msg = ""
    else:
        if report is None or report == "":
            today = timezone.now()
            days_remaining = (report_due_date - today).days
            if days_remaining < 0:  # If the report is overdue
                warning = True
                warning_msg = "Report overdue"
            elif days_remaining == 0:  # If the report is due today
                warning = True
                warning_msg = "Report due today"
            elif days_remaining == 1:  # If the report is due tomorrow
                warning = True
                warning_msg = "Report due tomorrow"
            elif (
                days_remaining > 1 and days_remaining <= 3
            ):  # If the report is due in less than 3 days
                warning = True
                warning_msg = f"Report due in {days_remaining} days"
            else:
                warning = False
                warning_msg = ""
        else:
            warning = False
            warning_msg = ""

    return warning, warning_msg


def upload_report_location(instance, filename):
    """
    Function to upload the report to the media folder
    The structre of the folder is reports/{semester_id}/{experiment_id}/
    """
    ext = filename.split(".")[-1]  # get the file extension
    new_filename = f"{instance.student.username}_{instance.experiment.id}_report.{ext}"
    semester_id = instance.semester.id  # semester ID e.g. SS2024
    experiment_id = instance.experiment.id  # experiment ID e.g. A1
    # Return the path relative to MEDIA_ROOT to save the file
    return f"reports/{semester_id}/{experiment_id}/{new_filename}"


def get_tags(richtext, delimiter="\r\n"):
    """
    Function to find all the tags in the rich text
    """
    tags = []
    tags_index = []
    # If the richtext is empty return the empty tag list
    if richtext is None or richtext == "":
        return tags, tags_index

    # If the richtext is not empty then get tags and their index
    else:
        # Split the richtext into separate lines based on the delimiter
        lines = richtext.split(delimiter)
        for line in lines:
            # If the line starts with <h1> then it is a tag
            if line.startswith("<h1>"):
                # Get the tag name and add it to the tags list
                tag = line.replace("<h1>", "").replace("</h1>", "")
                tags.append(tag)

                # Get the index of the tag and append
                tags_index.append(lines.index(line))

        # Add the end of text tag and its index to the list as well
        tags.append("End of text")
        tags_index.append(len(lines))

        return tags, tags_index


def parse_text(richtext, startpos, endpos, delimiter="\r\n"):
    """
    Function to parse text between two tag positions in richtext.
    """
    parsed_text = ""
    if richtext is None or richtext == "":
        return parsed_text
    else:
        lines = richtext.split(delimiter)  # Split the richtext into lines

        # if startpos is None, set it to 0
        if startpos is None:
            startpos = 0

        # if endpos is None, set it to the length of the lines
        if endpos is None:
            endpos = len(lines)

        # Get the text between the start and end positions
        for i in range(startpos, endpos):
            parsed_text += lines[i] + delimiter
        return parsed_text


def get_context(richtext):
    """
    Function to parse the richtext and return the context dictionary
    """
    context = {}  # Initialize the context dictionary

    # if the richtext is empty then return the empty context
    if richtext is None or richtext == "":
        context = {
            "Description": "No description available.",
        }
        return context

    # If the richtext is not empty then parse the richtext
    else:
        # Get all the tags in the richtext
        tags, tag_index = get_tags(richtext)
        # If there are no tags in the richtext return the full text as the description
        if len(tags) == 1:
            context = {
                "Description": richtext,
            }

        # If there is only one tag in the richtext
        elif len(tags) == 2:
            context[tags[0]] = parse_text(richtext, tag_index[0] + 1, None)

        # If there are multiple tags in the richtext
        else:
            for i in range(0, len(tags) - 1):
                parsed_text = parse_text(richtext, tag_index[i] + 1, tag_index[i + 1])
                context[tags[i]] = parsed_text

        return context
