Code Review Motivation
======================
Code review helps identify and correct errors, bugs, and vulnerabilities in the code. By having multiple sets of eyes examine the code, it becomes more robust and less prone to issues.

Code review provides an opportunity for knowledge sharing and collaboration. The author can gain insights and suggestions from the reviewer, while the reviewer can learn different approaches or techniques employed by the author.

When multiple team members contribute to a codebase, there is a reduced risk of knowledge silos or dependencies on a single person. If someone is unavailable or leaves the team, others can pick up the work and continue without major disruptions.

Goals
=====
1. **Operationally Ready:** The team's focus has transitioned from developing code primarily for research purposes to delivering production-ready code that is reliable, efficient, and meets the functional requirements of the system.

2. **Maturation:** The team aims to deliver high-quality code that enhances the existing functionality, introduces new features, and resolves any identified bugs or issues.

3. **Quality Control:** Code reviews play a crucial role in enhancing the overall quality of the team's codebase. Through constructive feedback and suggestions during the review process, the codebase can be continuously improved and refined.

    a. Code review is a more time-efficient process compared to writing code from scratch. Reviewing code allows the team to catch and address potential issues early, saving time and effort in the long run.

    b. The code review stage represents progress and advancement for the team. It signifies that the code is being thoroughly examined and refined, contributing to the overall improvement of the team's development practices.

    c. Code review is considered more important than writing code because it ensures the code's quality, correctness, and adherence to best practices. Reviewing code helps prevent issues from being introduced into the codebase, leading to a more stable and maintainable system.
    
Style and Process
=================
1. **Style Issues:** Style-related concerns should be addressed based on an established style guide. The style guide serves as a reference for consistent code formatting, naming conventions, and other stylistic aspects.

    a. If any issues arise that are not covered by the style guide, it is important to update the guide to include those specific scenarios. This ensures that the style guide remains comprehensive and up to date.

2. **Merging:** The code's author is responsible for merging the code into the main branch only after receiving approval from the reviewer(s). This ensures that the code has undergone proper review and meets the necessary quality criteria before being integrated into the codebase.

3. **Improvement:** The goal of code review is to improve the code, not to achieve perfection. While striving for high-quality code, the focus should be on identifying and addressing issues, enhancing functionality, and ensuring maintainability rather than pursuing an unattainable state of perfection.

4. **Objectives:** Code reviews typically aim to fix bugs, add new features, and clean up code to improve its maintainability. These objectives ensure that the codebase evolves continuously and aligns with the team's goals.

5. **Process:** Code review will begin with a GitHub pull request where the review or reviewers will be specified in a task. The reviewer may be a more senior engineer however it is best if they are not. A meeting should be scheduled between the author and reviewers if the code review is not easily resolved.

GitHub
======
1. **Pull Request:** Code review is initiated by creating a Pull Request in the chosen version control system, such as GitHub. The PR provides a context for changes made to the code and enables reviewers to review and provide feedback effectively.

2. **Avoid Main Branch:** To maintain code quality and ensure proper review, it is important to refrain from directly pushing code to the main branch. All code changes should go through the review process before being merged into the main branch.

3. **Reviewer's Acceptance:** Code changes from the main branch should not be merged without the reviewer's acceptance. This ensures that all code modifications have undergone thorough review and have received approval.

4. **Branching:** New code should be developed in separate branches, referred to as side branches or feature branches. This practice allows developers to work on isolated changes without directly impacting the main codebase.

    a. Once a side branch has been merged into the main branch, it is best practice to delete the side branch. This helps maintain a clean branch structure and prevents unnecessary clutter in the repository.

    b. Best practices for naming branches::
    
        feature/<name_or_description> ie. feature/das_add_rmq
        bug/<description> ie. bug/fix_rmq_connection
        Linear Issue Number ie. IDSSE-183

Author's Checklist
==================
* Ensuring adherence to the style guide

    The code author is responsible for ensuring that the code follows the guidelines outlined in the style guide. Consistency in code formatting and naming conventions is essential for readability and maintainability.

* Including docstrings

    Docstrings, which provide documentation and descriptions of functions, classes, and modules, should be included in the code. Well-written docstrings improve code comprehensibility and facilitate future maintenance.

* Passing linter checks

    The code should pass the linter checks defined for the project. Linters analyze code for potential errors, stylistic inconsistencies, and adherence to coding standards.

* Sufficient test code

    The code author should ensure that an adequate amount of test code is included. Each public function or method should have at least one corresponding test case to verify its functionality.

* Building and running code with Docker

    The code should be verified to build and run successfully within the project's Docker environment. Docker provides a consistent and reproducible execution environment for the codebase.

* Aim for manageable review time

    The code changes made by the author should be designed to be reviewable within a reasonable timeframe, ideally not taking more than one hour for the reviewer to assess. Keeping changes small and focused helps the reviewer to concentrate on specific aspects and provide timely feedback.

* Breaking down large code base changes

    If making significant changes to the codebase, it is advisable to break them down into smaller, manageable reviews. This approach allows for more focused and effective code review, reducing the chances of missing important details.

* Pull request title and summary

    The title of the Pull Request should indicate the significance and relevance of the code changes. The summary should provide helpful context and insights for the reviewer, such as the author's thought process, areas of concern, or specific parts they would like feedback on.

    Title should not start with “Adds”, “Deletes”, or “Updates”

* Review brevity

    The reviewer's time is valuable and the code review process should be kept as simple and easy as possible.
    
Reviewer's Guidelines
=====================
1. **Learning Opportunity:** Reviewers should view code reviews as a chance to enhance their knowledge and understanding. Instead of focusing solely on finding bugs, the primary objective should be to help improve the code and contribute to the team's growth.

2. **Team Improvement:** The reviewer's role is to assist in improving the code quality and promoting collaboration within the team. Providing constructive feedback, suggestions, and recommendations helps the team progress collectively.

3. **Two Passes:** The reviewer should conduct at least two passes when reviewing new code. The first pass should focus on understanding the high-level structure and logic, while the second pass delves into the details and identifies specific areas for improvement.

4. **Feedback:** When providing feedback, it is advisable to phrase comments as questions rather than making direct statements using "You." This approach encourages collaboration and helps to avoid sounding overly critical. Instead of saying, "You should rename this," consider using "Could this be renamed?"

5. **Providing Suggestions:** Instead of solely pointing out issues, the reviewer should provide suggestions for improvement and explain why the alternative approach is better. This helps the author understand the rationale behind the suggestions and fosters a learning environment.

6. **Highlight Positives:** It is beneficial to identify and document positive aspects of the code during the review process. Acknowledging good practices, elegant solutions, or improvements made by the author helps maintain a positive and constructive atmosphere.

7. **Granting Approval:** If the remaining fixes or changes requested are minor or trivial in nature, the reviewer can grant approval for the code to be merged. This acknowledges that the majority of the issues have been addressed and prevents unnecessary delays in the development process.

What to Look for
----------------
During the code review process, reviewers should focus on the following aspects:

1. **Obvious Bugs:** Identifying and addressing any apparent bugs or errors in the code is essential for maintaining the codebase's reliability and functionality.

2. **Possible Security Issues:** Reviewers should pay attention to potential security vulnerabilities in the code. This includes checking for proper input validation, protection against injection attacks, and adherence to security best practices.

3. **"Clever" Code:** Reviewers should be cautious of code that prioritizes clever or complex solutions over readability and maintainability. Ensuring that code is understandable and follows best practices is crucial for long-term maintenance.

4. **Code Duplication:** Identifying instances of code duplication and suggesting ways to refactor or reuse code can improve maintainability, reduce the risk of inconsistencies, and enhance overall efficiency.

5. **Descriptive Naming:** Reviewers should evaluate whether the names used for variables, functions, and classes are descriptive enough to convey their purpose and functionality. Clear and meaningful names contribute to code comprehensibility.

6. **Performance Improvements:** Reviewers should assess the code for potential performance bottlenecks or inefficiencies. Suggesting optimizations or alternative approaches can lead to improved system performance.

7. **Quality of Tests:** Reviewers should review the test code to ensure it provides adequate coverage and effectively verifies the functionality of the code under review. High-quality tests help prevent regressions and build confidence in the codebase.

What NOT to Look for
--------------------
Reviewers should avoid focusing on the following aspects during code reviews:

1. **Cosmetic Concerns:** Minor formatting issues, such as indentation or spacing inconsistencies, should not be the primary focus during code reviews. These can be addressed separately or enforced through automation.

2. **Testing:** Detailed testing should not be a primary concern during code reviews. While ensuring sufficient test coverage is important, the primary goal of a code review is to evaluate the quality and functionality of the code itself.

3. **Automation:** Code review is a human-centric process and should primarily focus on aspects that require human judgment and analysis. Issues that can be easily detected and addressed through automation, such as linting or syntax checks, should not be the primary focus during code reviews.

Addressing Related Issues:

If the reviewer identifies issues related to style guide violations, testing standards, or automation needs, these concerns should be addressed separately from the code review. They can be discussed in team meetings, documented for future updates to the style guide or testing framework, or raised as separate tasks or issues. It is important to address these concerns in a separate time and place to ensure a focused and efficient code review process.
