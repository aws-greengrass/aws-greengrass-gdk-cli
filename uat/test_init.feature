Feature: gdk test init works

    @version(min='1.3.0')
    @change_cwd
    Scenario: init test in an existing gdk project
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
    Scenario: test-e2e-init-2: Initialize a GDK project with an end-to-end testing module using a specific version of OTF
        Given we have cli installed
        When we run gdk component init -t HelloWorld -l python -n test-dir
        Then command was successful
        And we change directory to test-dir
        And change component name to com.example.PythonHelloWorld
        And we verify gdk project files
        When we run gdk test-e2e init --otf-version 1.2.0
        Then we verify gdk test files
        Then we verify that the OTF version used is 1.2.0

    @version(min='1.3.0')
    @change_cwd
    Scenario: test-e2e-init-3: When a GDK project with an existing e2e testing module is initialized again using test-e2e init command, the command exits without overrding any files.
        Given we have cli installed
        When we run gdk component init -t HelloWorld -l python -n test-dir
        Then command was successful
        And we change directory to test-dir
        And change component name to com.example.PythonHelloWorld
        And we verify gdk project files
        When we run gdk test-e2e init --otf-version 1.2.0
        Then we verify gdk test files
        When we run gdk test-e2e init --otf-version 1.3.0
        Then we verify that the OTF version used is 1.2.0
