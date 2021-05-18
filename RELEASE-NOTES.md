# 0.0.2

## Notable Changes
* Added modules for firmware_management, rapids, topology and user_management
* Major update to existing config_apsettings_from_csv.py workflow. It accepts CSV file downloaded from the Central UI group. This workflow also generates a new CSV file with failed APs. CSV file format from the previous version is not backward compatible.
* Fixes and improvement to existing modules, utilities and the documentation
* Merged PRs and resolved GitHub issues:
    - PR #6: example AP rename code always terminates with an error
    - PR #2: fix url concat in command()
    - PR #1: Added the ability for multiple Aruba Central account's in the config file and passed to pycentral

## Known Issues
* No known issues.

# 0.0.1

## Notable Changes
* This is the initial release for the Aruba Central Python SDK, sample scripts, and workflows.

## Known Issues
* No known issues.
