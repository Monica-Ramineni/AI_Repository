# How to Merge `S03-EndtoEndRAG` Feature Branch into `main`

## Option 1: GitHub Pull Request (Recommended)

1. Go to the repository on GitHub: [AI_Repository](https://github.com/Monica-Ramineni/AI_Repository)
2. You should see a prompt to create a pull request for `S03-EndtoEndRAG` (or click "Compare & pull request").
3. Review the changes, add a description, and click **Create pull request**.
4. After review, click **Merge pull request** and confirm the merge.
5. (Optional) Delete the `S03-EndtoEndRAG` branch after merging.

---

## Option 2: GitHub CLI

1. Make sure you have the [GitHub CLI](https://cli.github.com/) installed and authenticated.
2. In your terminal, run:

```sh
git fetch origin
# Create the PR from the feature branch
gh pr create --base main --head S03-EndtoEndRAG --title "End-to-End RAG Feature" --body "Adds PDF upload, indexing, and RAG chat using aimakerspace library."
# (Optional) Merge the PR after review
gh pr merge --merge
```

---

**Summary:**
- This feature branch adds PDF upload, indexing, and RAG chat using the aimakerspace library to both the backend (FastAPI) and frontend (Next.js).
- Please review the changes before merging. 