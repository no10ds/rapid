# 0009 - Handle large files [Upload]

Date: 2022-09-07

## Status

Accepted

## People Involved

Lewis Card, Claude Paret, Cristhian Da Silva, Lydia Adejumo, Shashin Dayanand, Jowita Podolak

## Context

Uploadable file sizes are limited by the size of the memory allocated to the task in ECS. By default, this stands at
500MB, meaning the largest dataset that could be handled is around 400-500MB.

Increasing the task memory is an option but very quickly becomes prohibitively expensive.

This is clearly unacceptable in the longer term.

## Decision

File upload will broadly be handled as follows:

- The uploaded file is streamed and saved into the task file storage disk (current default is 20GB but is scalable)
- The file is processed asynchronously in the background
- The uploaded raw file is deleted

## Consequences

- The largest file that can be handled is around 20GB without scaling the persistent storage outwards.
- File upload proceeds in the background so a mechanism is required for users to check the progress of their upload (
  success, failure or in-progress)
