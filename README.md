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

## To do

- Reconciliation script - to be run daily, to report changes. I have used the JumpCloud host ID field and populate the Snipe IT custom field with this ID, so that the reconcilliation script can use this rather than a hostname match. Also has benefit of allowing manual entry of JC agent ID to Snipe IT field, so that machines can be paired. This is in progress.
- Onboarding script - currently working on script to set up new user in JC, create new user in Snipe, assign laptop, create Google Workspace account.
