# 0003 - Consolidated Pipeline Job
Date: 2022-03-13

## Status
Accepted

## Context

Initially we defined the 'pipeline' in Github Actions as a `workflow` with multiple `jobs`, each of which
had a set of `steps` within it.

The runtime environment (i.e.: the runner executing the tasks) is only guaranteed to be the same within a job; that is, for all steps inside a job.

Since we were using a single self-hosted runner this behaviour was implicitly extended across different jobs.

However, when commits were made in quick succession and multiple pipeline runs were scheduled, we found that the individual jobs would interleave:
```text
Workflow1-Job1-StepsX-Y
    Workflow2-Job1-StepsX-Y
Workflow1-Job2-StepsX-Y
    Workflow2-Job2-StepsX-Y
...
```

Desired:
```text
Workflow1-JobX-Y-StepsX-Y

Workflow2-JobX-Y-StepsX-Y
```


Since these would all run on the same runner (for us an EC2 instance), it was possible to have the pipeline build an image
and then run tests from the next pipeline run (the newer version) before resuming the tests from the first run.

Therefore, there was often uncertainty as to which version was tested, tagged and deployed.

## Decision

We decided to combine all the sub `steps` from each `job` into one large `job`.

## Consequences

Since Github Actions guarantee that all `steps` inside a `job` will execute sequentially and on the same runner
this ensures that `workflow` runs will be sequential and that any interleaving will be avoided.
