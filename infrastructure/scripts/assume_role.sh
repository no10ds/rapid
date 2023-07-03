#!/usr/bin/env bash
set -eu -o pipefail

function ask_mfa_from_user() {
   read -r ACCOUNT USER_ARN <<<"$(aws sts get-caller-identity |jq -rj '.Account," ",.Arn')"
   USER_NAME="$(echo "$USER_ARN" |awk -F/ '{print $2}')"
   echo "Enter MFA for user $USER_NAME in profile ${AWS_PROFILE}: "
   read -rs MFA
   printf " (mfa: %s )\n" "$MFA"
}

function ask_target_role_from_user() {
   printf "Select role to assume:\n\t1: resource-user\n\t2: resource-admin\n"
   read -r TARGET_ROLE
   case "$TARGET_ROLE" in
      1)
         ROLE="role/resource-user"
         ;;
      2)
         ROLE="role/resource-admin"
         ;;
      *)
         echo "Please select 1 or 2" && exit 1
   esac
   printf " (selected role %s)\n\n" "$ROLE"
}

function assume_role_and_echo_creds() {
   printf "\nAttempting to assume role ...\n"
   read -r AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN \
      <<<"$(aws sts assume-role --role-arn "arn:aws:iam::$ACCOUNT:$ROLE" \
            --role-session-name my_admin_session \
            --serial-number "arn:aws:iam::$ACCOUNT:mfa/${USER_NAME}" --token-code "$MFA"\
            | jq -jr '.Credentials.AccessKeyId," ",.Credentials.SecretAccessKey," ",.Credentials.SessionToken')"

   export AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID"
   export AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY"
   export AWS_SESSION_TOKEN="$AWS_SESSION_TOKEN"
   aws sts get-caller-identity |jq
   printf "\nYou need to export these vars - just copy and paste\n"
   echo "export AWS_ACCESS_KEY_ID=\"$AWS_ACCESS_KEY_ID\""
   echo "export AWS_SECRET_ACCESS_KEY=\"$AWS_SECRET_ACCESS_KEY\""
   echo "export AWS_SESSION_TOKEN=\"$AWS_SESSION_TOKEN\""
}

main () {
   ask_target_role_from_user
   ask_mfa_from_user
   assume_role_and_echo_creds
}

main
