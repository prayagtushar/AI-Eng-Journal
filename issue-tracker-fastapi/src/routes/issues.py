import uuid
from fastapi import APIRouter, HTTPException
from src.db.schema import CreateIssue, UpdateIssue, IssueResponse
from src.storage.storage import load_data, save_data

router = APIRouter(prefix="/api/v1/issues", tags=["issues"])

@router.post('/create', response_model=IssueResponse)
def create_new_issue(payload : CreateIssue):
    """ Create New Issue """
    issues = load_data()

    newIssue = {
        "id" : uuid.uuid4(), 
        "title" : payload.title(),
        "description" : payload.description(),
        "priority" : payload.priority()
    }

    issues.append(newIssue)
    save_data(issues)

    return issues

@router.get('/')
def get_issues(): 
    """ Get all the existing issues """
    issues = load_data()
    return issues


@router.get('/{{issue_id}}')
def get_issue_byId(issue_id : int):
    """ Get Issue by ID """
    issues = load_data()

    for issue in issues:
        if(issue["id"] == issue_id):
            return issue
    raise HTTPException(detail = "Issue not found")

@router.put('/{issue_id}')
async def update_issue(issue_id : int,payload : UpdateIssue):
    """ Update an issue """

    issues = load_data()
    for issue in issues:
        if issue["id"] == issue_id:
            if payload.title is not None:
                issue["title"] = payload.title
            if payload.description is not None:
                issue["description"] = payload.description
            if payload.priority is not None:
                issue["priority"] = payload.priority.value

            save_data(issues)
            return "Issue updated successfully"
    
    raise HTTPException(detail="Issue not found")

@router.delete("/{issue_id}")
def delete_issue(issue_id: str):
    """Delete an issue by ID."""

    issues = load_data()

    for i, issue in enumerate(issues):
        if issue["id"] == issue_id:
            issues.pop(i)
            save_data(issues)
            return

    raise HTTPException(detail="Issue not found")