# encoding: utf-8

import sys
import argparse
from urllib.parse import urljoin
from workflow import Workflow, web, PasswordNotFound

API_BASE_URL = 'http://gitlab.alibaba-inc.com/api/v3/'
ICON_REPO = "./icons/repo.png"
ICON_ERROR = "./icons/error.png"

def parse_opt():
    # build argument parser to parse script args and collect their
    # values
    parser = argparse.ArgumentParser()
    parser.add_argument('--set-token', dest='private_token', nargs='?', default=None)
    # add an optional query and save it to 'query'
    parser.add_argument('query', nargs='?', default=None)
    # parse the script's arguments
    return parser.parse_args(wf.args)


def main(wf):
    args = parse_opt()

    # optional set private_token
    if args.private_token:
        wf.save_password('gitlab_private_token', args.private_token)
        return 0  # 0 means script exited cleanly

    # Check that we have an PRIVATE_TOKEN saved, otherwise return
    try:
        private_token = wf.get_password('gitlab_private_token')
    except PasswordNotFound:
        wf.add_item('No private token set.',
                    'Please use gltoken to set your GitLab private token.',
                    valid=False,
                    icon=ICON_ERROR)
        wf.send_feedback()
        return 0

    # Get project from gitlab
    url = urljoin(API_BASE_URL, "projects")
    params = dict(private_token=private_token, 
                  order_by="last_activity_at",
                  search=args.query or "")
    wf.logger.debug(f"get project from {url} with params: {params}")
    r = web.get(url, params)
    # throw an error if request failed
    # Workflow will catch this and show it to the user
    r.raise_for_status()
    # Parse the JSON returned by gitlab
    projects = r.json()

    if not projects:
        wf.add_item('No projects found', icon=ICON_REPO)
        wf.send_feedback()
        return 0

    # Loop through the returned posts and add an item for each to
    # the list of results for Alfred
    for project in projects:
        # NOTE: replace code.alibaba-inc.com/ to gitlab.alibaba-inc.com/ in the url
        project['web_url'] = project['web_url'].replace("code.alibaba-inc.com/", "gitlab.alibaba-inc.com/")

        wf.add_item(title=project['path'],
                    subtitle=project['path_with_namespace'],
                    arg=project['web_url'],
                    autocomplete=project['path'],
                    valid=True,
                    icon=ICON_REPO)

    # Send the results to Alfred as XML
    wf.send_feedback()


if __name__ == u"__main__":
    wf = Workflow()
    sys.exit(wf.run(main))