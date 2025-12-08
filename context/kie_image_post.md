POST
/api/v1/jobs/createTask
Create Task
Create a new generation task

Request Parameters
The API accepts a JSON payload with the following structure:

Request Body Structure
{
  "model": "string",
  "callBackUrl": "string (optional)",
  "input": {
    // Input parameters based on form configuration
  }
}
Root Level Parameters
model
Required
string
The model name to use for generation

Example:

"google/nano-banana"
callBackUrl
Optional
string
Callback URL for task completion notifications. Optional parameter. If provided, the system will send POST requests to this URL when the task completes (success or failure). If not provided, no callback notifications will be sent.

Example:

"https://your-domain.com/api/callback"
Input Object Parameters
The input object contains the following parameters based on the form configuration:

input.prompt
Required
string
The prompt for image generation

Max length: 5000 characters
Example:

"A surreal painting of a giant banana floating in space, stars and galaxies in the background, vibrant colors, digital art"
input.output_format
Optional
string
Output format for the images

Available options:

png
-
PNG
jpeg
-
JPEG
Example:

"png"
input.image_size
Optional
string
Radio description

Available options:

1:1
-
1:1
9:16
-
9:16
16:9
-
16:9
3:4
-
3:4
4:3
-
4:3
3:2
-
3:2
2:3
-
2:3
5:4
-
5:4
4:5
-
4:5
21:9
-
21:9
auto
-
auto
Example:

"1:1"
Request Example

Python
curl -X POST "https://api.kie.ai/api/v1/jobs/createTask" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "model": "google/nano-banana",
    "callBackUrl": "https://your-domain.com/api/callback",
    "input": {
      "prompt": "A surreal painting of a giant banana floating in space, stars and galaxies in the background, vibrant colors, digital art",
      "output_format": "png",
      "image_size": "1:1"
    }
}'
Response Example
{
  "code": 200,
  "message": "success",
  "data": {
    "taskId": "task_12345678"
  }
}
Response Fields
code
Status code, 200 for success, others for failure
message
Response message, error description when failed
data.taskId
Task ID for querying task status
Callback Notifications
When you provide the callBackUrl parameter when creating a task, the system will send POST requests to the specified URL upon task completion (success or failure).

Success Callback Example
{
    "code": 200,
    "data": {
        "completeTime": 1755599644000,
        "consumeCredits": 100,
        "costTime": 8,
        "createTime": 1755599634000,
        "model": "google/nano-banana",
        "param": "{\"callBackUrl\":\"https://your-domain.com/api/callback\",\"model\":\"google/nano-banana\",\"input\":{\"prompt\":\"A surreal painting of a giant banana floating in space, stars and galaxies in the background, vibrant colors, digital art\",\"output_format\":\"png\",\"image_size\":\"1:1\"}}",
        "remainedCredits": 2510330,
        "resultJson": "{\"resultUrls\":[\"https://example.com/generated-image.jpg\"]}",
        "state": "success",
        "taskId": "e989621f54392584b05867f87b160672",
        "updateTime": 1755599644000
    },
    "msg": "Playground task completed successfully."
}
Failure Callback Example
{
    "code": 501,
    "data": {
        "completeTime": 1755597081000,
        "consumeCredits": 0,
        "costTime": 0,
        "createTime": 1755596341000,
        "failCode": "500",
        "failMsg": "Internal server error",
        "model": "google/nano-banana",
        "param": "{\"callBackUrl\":\"https://your-domain.com/api/callback\",\"model\":\"google/nano-banana\",\"input\":{\"prompt\":\"A surreal painting of a giant banana floating in space, stars and galaxies in the background, vibrant colors, digital art\",\"output_format\":\"png\",\"image_size\":\"1:1\"}}",
        "remainedCredits": 2510430,
        "state": "fail",
        "taskId": "bd3a37c523149e4adf45a3ddb5faf1a8",
        "updateTime": 1755597097000
    },
    "msg": "Playground task failed."
}