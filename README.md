# Learnings
* GPT-3.5 doesn't do a good job generating pandas code
* Context window constraints happen fairly easily for large bases.  go/launchpad has a single row with 9k tokens.  We should prevent full row or multi row queries via the prompt.
* Queries are looong