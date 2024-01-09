Feature: As a component builder, I can run `gdk test-e2e init` command to initialize an existing GDK project with the testing module that uses GTF.

    @version(min='1.3.0')
    @change_cwd
    Scenario: test-e2e-init-1: Initialize a GDK project with an e2e testing module with default configuration and no commmand args
        Given we have cli installed
        When we run gdk component init -t HelloWorld -l python -n test-dir
        Then command was successful
        And we change directory to test-dir
        And change component name to com.example.PythonHelloWorld
        And we verify gdk project files
        When we run gdk test-e2e init
        Then we verify gdk test files


    @version(min='1.3.0')
    @change_cwd
    Scenario: test-e2e-init-2: Initialize a GDK project with an end-to-end testing module using a specific version of GTF
        Given we have cli installed
        When we run gdk component init -t HelloWorld -l python -n test-dir
        Then command was successful
        And we change directory to test-dir
        And change component name to com.example.PythonHelloWorld
        And we verify gdk project files
        When we run gdk test-e2e init --otf-version 1.0.0
        Then we verify gdk test files
        Then we verify that the GTF version used is 1.0.0

    @version(min='1.3.0')
    @change_cwd
    Scenario: test-e2e-init-3: When a GDK project with an existing e2e testing module is initialized again using test-e2e init command, the command exits without overrding any files.
        Given we have cli installed
        When we run gdk component init -t HelloWorld -l python -n test-dir
        Then command was successful
        And we change directory to test-dir
        And change component name to com.example.PythonHelloWorld
        And we verify gdk project files
        When we run gdk test-e2e init --otf-version 1.1.0
        Then we verify gdk test files
        When we run gdk test-e2e init --otf-version 1.0.0
        Then we verify that the GTF version used is 1.1.0


    @version(min='1.3.0')
    @change_cwd
    Scenario: test-e2e-init-4: When I initialize a GDK project with an e2e testing module using a version of GTF that doesn't exist, the command exits with an error
        Given we have cli installed
        When we run gdk component init -t HelloWorld -l python -n test-dir
        Then command was successful
        And we change directory to test-dir
        And change component name to com.example.PythonHelloWorld
        And we verify gdk project files
        When we run gdk test-e2e init --otf-version 10.0.0
        Then command was unsuccessful
        Then command output contains "'10.0.0' does not exist"
