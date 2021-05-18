# Contribution Guidelines

If you're reading this, you're probably thinking about contributing to this repository. We really appreciate that--thank you!

This document provides guidelines on contributing to this repository. Please follow these guidelines when creating issues, making commits, and submitting pull requests. The repository maintainers review all pull requests and verify that they conform to these guidelines before approving and merging.

#### Table Of Contents
[How Can I Contribute?](#how-can-i-contribute)
  * [Contribution Ideas](#contribution-ideas)
  * [What should I know before I get started?](#what-should-i-know-before-i-get-started)

[Licensing](#licensing)
  * [Developer's Certificate of Origin](#developers-certificate-of-origin)
  * [Sign Your Work](#sign-your-work)

[Coding Conventions](#coding-conventions)

[Additional Notes](#additional-notes)
  * [Resources](#resources)

## How Can I Contribute?

### Contribution Ideas

1. Raise issues for bugs, features, and enhancements.
1. Submit updates and improvements to the documentation.
1. Submit articles and guides, which are also part of the documentation.
1. Help out repo maintainers by answering questions in [Airheads Developer Community][airheads-link].
1. Share feedback and let us know about interesting use cases in [Airheads Developer Community][airheads-link].

### What should I know before I get started?

The best way to directly collaborate with the project contributors is through GitHub.

* If you want to raise an issue such as a defect, an enhancement request, feature request, or a general issue, please open a GitHub issue.
* If you want to contribute to our code by either fixing a problem, enhancing some code, or creating a new feature, please open a GitHub pull request against the development branch.
> **Note:** All pull requests require an associated issue number, must be made against the **development** branch, and require acknowledgement of the DCO. See the [Licensing](#licensing) section below.

Before you start to code, we recommend discussing your plans through a GitHub issue, especially for more ambitious contributions. This gives other contributors a chance to point you in the right direction, give you feedback on your design, and help you find out if someone else is working on the same thing.

It is your responsibility to test and verify, prior to submitting a pull request, that your updated code doesn't introduce any bugs. Please write a clear commit message for each commit. Brief messages are fine for small changes, but bigger changes warrant a little more detail (at least a few sentences).
Note that all patches from all contributors get reviewed.
After a pull request is made, other contributors will offer feedback. If the patch passes review, a maintainer will accept it with a comment.
When a pull request fails review, the author is expected to update the pull request to address the issue until it passes review and the pull request merges successfully.

At least one review from a maintainer is required for all patches.

### Contribution Guidelines
This repo is maintained on a best-effort basis. The burden is on the submitter and not the repo maintainers to ensure the following criteria are met when code is submitted.
1. All code submissions must adhere to the structure of the repo:
    * Directory /pycentral holds python libraries and /workflows directory.
    * The library files are base/low-level API calls with each file relating to a category in the API Documentation page within the Aruba Central API Gateway.
    * High-level process/use-case focused scripts must be placed in the /workflows directory.
    * Sample Scripts should be placed in /sample_scripts directory.
    * Do not create new separate directory for submitted projects.
    * Do not make copies of existing files to be saved in different folders.
2. All Python code should conform to liberal PEP-8 standards.
3. All functions should have explanatory docstrings using the reStructuredText format.
4. All workflows should have a comment at the top explaining the configuration steps the workflow performs, and any preconditions that need to be met before running the script.
5. All git commits should have clear, concise messages which explain the changes made in the commit. All Pull Requests (PRs) should contain a title and comments that explain the impact of the PR.
6. All code submitted for merge consideration must be tested by the submitter.

## Licensing

All contributions must include acceptance of the DCO:

### Developer’s Certificate of Origin

> Developer Certificate of Origin Version 1.1
>
> Copyright (C) 2004, 2006 The Linux Foundation and its contributors. 660
> York Street, Suite 102, San Francisco, CA 94110 USA
>
> Everyone is permitted to copy and distribute verbatim copies of this
> license document, but changing it is not allowed.
>
> Developer's Certificate of Origin 1.1
>
> By making a contribution to this project, I certify that:
>
> \(a) The contribution was created in whole or in part by me and I have
> the right to submit it under the open source license indicated in the
> file; or
>
> \(b) The contribution is based upon previous work that, to the best of my
> knowledge, is covered under an appropriate open source license and I
> have the right under that license to submit that work with
> modifications, whether created in whole or in part by me, under the same
> open source license (unless I am permitted to submit under a different
> license), as indicated in the file; or
>
> \(c) The contribution was provided directly to me by some other person
> who certified (a), (b) or (c) and I have not modified it.
>
> \(d) I understand and agree that this project and the contribution are
> public and that a record of the contribution (including all personal
> information I submit with it, including my sign-off) is maintained
> indefinitely and may be redistributed consistent with this project or
> the open source license(s) involved.

### Sign Your Work

To accept the DCO, simply add this line to each commit message with your
name and email address (`git commit -s` will do this for you):

    Signed-off-by: Jane Example <jane@example.com>

For legal reasons, no anonymous or pseudonymous contributions are
accepted.

## Coding Conventions

1. Python code should conform to PEP-8.
1. Since this is a collaborative project, document your code with comments that will help other contributors understand the code you write.
1. When in doubt, follow conventions you see used in the source already.

## Additional Notes

> **Note:** Please don't file an issue to ask a question. Please reach out to us via email or disucssion forums.

### Resources

| Resource | Description |
| --- | --- |
| [Airheads Developer Community][airheads-link] | Aruba Airheads forum to discuss all things network automation. |
| [Aruba Bots Automate Videos][aruba-bots-playlist-link]| YouTube playlist containing instructional videos for Ansible and Python automation repositories. |
| [aruba-automation@hpe.com][email-link] | Distribution list email to contact the switching automation technical marketing engineering team. |


[airheads-link]: https://community.arubanetworks.com/community-home/digestviewer?communitykey=ea467413-8db4-4c49-b5f8-1a12f193e959
[aruba-bots-playlist-link]: https://youtube.com/playlist?list=PLsYGHuNuBZcY02FUh95ZpOB5VFkPurVaX
[email-link]: mailto:aruba-automation@hpe.com
