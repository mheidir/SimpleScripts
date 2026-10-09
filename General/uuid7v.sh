# UUIDv7 Bash Functions
#
# These functions are derived from the PostgreSQL UUIDv7 SQL implementation available at:
# https://github.com/dverite/postgres-uuidv7-sql/blob/main/sql/uuidv7-sql--1.0.sql
# They were converted to bash using ChatGPT 4o with Canvas on October 13, 2024:
# https://chatgpt.com/share/670c2da8-59ec-8007-aa8e-fd5760133fe8
#
# UUIDv7 is designed to incorporate the current timestamp with randomness, providing both uniqueness and chronological sorting.
# This script provides Bash implementations to generate UUIDv7 values with millisecond and sub-millisecond precision,
# extract the timestamp from a UUIDv7 value, and generate a UUIDv7 boundary value.
#
# Usage Examples:
# uuidv7
# uuidv7_sub_ms
# uuidv7_extract_timestamp "your-uuidv7-here"
# uuidv7_boundary "2024-10-13 10:00:00"

# Function to generate a UUIDv7 value with millisecond precision
uuidv7() {
  # Get the current timestamp in milliseconds since the epoch
  local timestamp_ms=$(($(date +%s%3N)))

  # Generate a random UUID and replace the first 48 bits with the timestamp
  local uuid=$(uuidgen | tr '[:upper:]' '[:lower:]')

  # Set version to 7 and replace the first part of the UUID
  local uuidv7_hex=$(printf "%012x" "$timestamp_ms")
  echo "$uuid" | awk -v hex="$uuidv7_hex" \
    'BEGIN {FS="-"} {printf "%s-%s-7%s-%s-%s\n", substr(hex, 1, 8), substr(hex, 9, 4), substr($3, 2), $4, $5}'
}

# Function to generate a UUIDv7 value with sub-millisecond precision (Method 3 of the spec)
uuidv7_sub_ms() {
  # Get the current timestamp in milliseconds, including fractional parts
  local timestamp_ms=$(date +%s%3N.%N)
  local t_ms=${timestamp_ms%.*}
  local sub_ms=$(( (${timestamp_ms#*.} / 1000000) % 4096 ))

  # Generate a random UUID
  local uuid=$(uuidgen | tr '[:upper:]' '[:lower:]')

  # Set version to 7, replace timestamp and sub-ms part of the UUID
  local uuidv7_hex=$(printf "%012x" "$t_ms")
  local sub_ms_hex=$(printf "%03x" "$sub_ms")
  echo "$uuid" | awk -v hex="$uuidv7_hex" -v sub_hex="$sub_ms_hex" \
    'BEGIN {FS="-"} {printf "%s-%s-7%s-%s-%s\n", substr(hex, 1, 8), substr(hex, 9, 4), substr(sub_hex, 1, 3), $4, $5}'
}

# Function to extract the timestamp from the first 6 bytes of a UUIDv7 value
uuidv7_extract_timestamp() {
  local uuid=$1
  local uuid_bytes=$(echo "$uuid" | awk -F'-' '{print $1 $2}')
  local timestamp_ms=$((16#${uuid_bytes}))
  date -d @$(echo "scale=3; $timestamp_ms / 1000" | bc) +"%Y-%m-%d %H:%M:%S.%3N %Z"
}

# Function to generate a UUIDv7 boundary value with a given timestamp
uuidv7_boundary() {
  local timestamp=$1
  local timestamp_ms=$(($(date -d "$timestamp" +%s%3N)))

  # Set version to 7 and generate a UUID with all other fields set to 0
  local uuidv7_hex=$(printf "%012x" "$timestamp_ms")
  printf "%s-%s-7%s-8000-000000000000\n" \
    "${uuidv7_hex:0:8}" "${uuidv7_hex:8:4}" "${uuidv7_hex:12:3}"
}

# Function to generate a base62 from UUIDv7
uuidv7_to_base62() {
  python3 - "$1" <<'PY'
import sys

uuid = sys.argv[1].replace("-", "").lower()

if len(uuid) != 32 or any(c not in "0123456789abcdef" for c in uuid):
    raise SystemExit("invalid UUID")

n = int(uuid, 16)
alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

out = ""
while n:
    n, r = divmod(n, 62)
    out = alphabet[r] + out

# A 128-bit value needs at most 22 base62 characters.
print(out.rjust(22, "0"))
PY
}

uuid=$(uuidv7)
base62=$(uuidv7_to_base62 "$uuid")

printf '%s\n' "$base62"