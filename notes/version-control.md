# Version Control & Git Notes

## 1. What is Version Control?

Version control is a system that tracks changes made to files over time.

It helps developers:
- Track what changed and when.
- Return to an earlier version if something breaks.
- Work with other developers without losing each other's changes.
- Maintain a history of a project's development.

## 2. What is Git?

Git is a distributed version control system. It tracks changes to files and stores project history on my computer.

## 3. What is GitHub?

GitHub is an online platform for hosting Git repositories. It lets me store and share my code online and collaborate with other developers.

**Remember:** Git is the tool; GitHub is an online platform that uses Git.

## 4. What is a Repository?

A repository (repo) is a project folder whose files and change history are tracked by Git.

My project: CampusSpend — a student expense tracker.

## 5. The Git Workflow

Working directory → Staging area → Local repository → Remote repository

- **Working directory:** Where I edit my files.
- **Staging area:** Where I select changes for the next commit.
- **Local repository:** Where Git stores committed project history on my computer.
- **Remote repository:** The online copy hosted on GitHub.

## 6. Essential Git Commands

### Check project status
`git status`

Shows which files are modified, staged, untracked, or ready to commit.

### Stage a file
`git add main.py`

Selects changes in `main.py` to be included in the next commit.

### Commit changes
`git commit -m "Build basic expense tracker"`

Records the staged changes in the local repository with a descriptive message.

### Push changes
`git push`

Uploads local commits to the connected remote repository, such as GitHub.

### View commit history
`git log --oneline`

Displays a compact history of commits.

## 7. What Is a Commit?

A commit is a recorded snapshot of the staged changes in my project. It has a unique identifier and a message describing the changes.

## 8. What I Did Today

1. Created a basic expense tracker in Python.
2. Used Git to stage the Python file.
3. Created a commit with a descriptive message.
4. Pushed the commit to GitHub.

## 9. Important Distinction

`git add` does not upload files to GitHub.

`git commit` saves a snapshot locally.

`git push` sends committed changes to the remote repository.

## 10. My Rule

Before committing, I should inspect `git status`, stage only the changes I intend to include, and use a commit message that describes what changed.