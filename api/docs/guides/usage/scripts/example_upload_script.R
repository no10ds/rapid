library(httr)
library(jsonlite)
library(dplyr)
library(base64enc)
library(data.dataset)

# Change these values
URL <- "URL"
CLIENT_ID <- "CLIENT_ID"
CLIENT_SECRET <- "CLIENT_SECRET"
DOMAIN <- "demo"
DATASETS <- "demo"


# Set the dataframe
df <- data.frame(
Name = c("John", "Alice", "Bob"),
Age = c(25, 30, 35),
City = c("New York", "London", "Paris")
)

# Encode credentials
credentials <- paste(CLIENT_ID, CLIENT_SECRET, sep = ":")
encoded_credentials <- base64encode(charToRaw(credentials))

# Fetch auth token
res <- POST(
  url = paste0(URL, "/oauth2/token"),
  add_headers("Content-Type" = "application/x-www-form-urlencoded"),
  add_headers("Authorization" = paste("Basic ", encoded_credentials)),
  body = list("grant_type" = "client_credentials", "client_id" = CLIENT_ID),
  encode = "json"
)
token <- jsonlite::fromJSON(content(res, "text"))$access_token

print(paste("Uploading datatset:", DATASET))

# Write dataframe to a CSV file
filepath <- paste0("rapid-", DATASET, ".csv")
fwrite(df, file = filepath, sep = ",")

# Upload the CSV file as a form field
response <- POST(
url = paste0(URL, "/datasets/", DOMAIN, "/", DATASET),
add_headers("Authorization" = paste0("Bearer ", token)),
body = list(
    file = upload_file(filepath, type = "text/csv")
),
encode = "multipart"
)
data <- jsonlite::fromJSON(content(response, "text"))

print(response$status_code)
print(data)

# Remove the temporary CSV file
file.remove(filepath)

print("Script finished")
