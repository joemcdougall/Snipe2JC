# Snipe2JC
Scripts to integrate SnipeiIT with JumpCloud

## Things to improve

- Better error handling (works as fire and forget)
- Google Workspace webhook should be handled by SNS alongside email. Create AWS Lambda to handle Workspace alert

## How it works

1. Gets list of assets from Snipe-IT
2. Looks for assets whose name begins with my prefix (this is because all my work computers are named like ORG-LAP-111)
3. Checks JumpCloud for that hostname
4. If exists, gets RAM and CPU info from JumpCloud
5. Updates Snipe-IT with these values
6. Sends a report of errors by email (via AWS SNS) and to a Google Workspace webhook

## Notes

1. Make sure you add custom fields to Snipe-IT to store CPU and RAM info.
