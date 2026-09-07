# VLX_API_ENABLED=true
# VLX_API_ENDPOINT=http://172.16.37.118:8888/os/
# VLX_API_KEY=aaas_ondoYHbrL0IGkA7bXMEPsFKCtsQuPhFXLuB0XBXKukwtTNSoZ447EiEwkgDvchJB
# VLX_API_CONNECT_TIMEOUT_MS=60000
# VLX_API_READ_TIMEOUT_MS=60000
# VLX_API_WRITE_TIMEOUT_MS=60000

import os

os.environ["VLX_API_ENABLED"] = "true"
os.environ["VLX_API_ENDPOINT"] = "http://172.16.37.118:8000/os/"
os.environ["VLX_API_KEY"] = "YjI3YjM4OTQyZDczMjZkMWUzYTdAZVpHVWdxdzg="
os.environ["VLX_API_CONNECT_TIMEOUT_MS"] = "60000"
os.environ["VLX_API_READ_TIMEOUT_MS"] = "60000"
os.environ["VLX_API_WRITE_TIMEOUT_MS"] = "60000"

from omai_client import VlxApiClient

# 从环境变量读取配置，创建客户端
vlx_api_client = VlxApiClient.from_env()

# headers = {
#     "Authorization": "YjI3YjM4OTQyZDczMjZkMWUzYTdAZVpHVWdxdzg=",
# }

from omai_client import (
    VlxApiClient,
    VlxSeekRequest,
    VlxSeekMessage,
    VlxSeekContent,
    VlxSeekImageUrl,
)


# 请求 vlx-seek
image_url = VlxSeekImageUrl(
    url="https://airesources.oss-cn-hangzhou.aliyuncs.com/0924/fire.jpg"
)

image = VlxSeekContent(
    type="image_url",
    image_url=image_url,
)

text = VlxSeekContent(
    type="text",
    text="找到图中所有的：火。",
)

message = VlxSeekMessage(
    role="user",
    content=[image, text],
)

# bbox_list: [[28, 54, 481, 387]]
bbox_list = None

request = VlxSeekRequest(
    model="vlx-seek-1.5-3b",
    messages=[message],
    bbox_list=bbox_list,
    max_tokens=4096,
    temperature=0.0,
    top_p=1.0,
)

response = vlx_api_client.vlx_seek(request)
print("vlx_seek response:", response)
"""
vlx_seek response: VlxSeekResponse(id='01m1x93eb4s5c3vxrsmyf7bmny', object='chat.completion', created=1788762766, model='vlx-seek-1.5-3b', choices=[VlxSeekChoice(index=0, message=VlxSeekMessageResult(role='assistant', content='<ground>火</ground><objects>None</objects>'), logprobs={}, finish_reason='stop', result_bbox_list=[], raw={'index': 0, 'message': {'role': 'assistant', 'content': '<ground>火</ground><objects>None</objects>', 'reasoning_content': ''}, 'logprobs': {}, 'finish_reason': 'stop', 'result_bbox_list': []})], usage=VlxSeekUsage(prompt_tokens=767, total_tokens=774, completion_tokens=7, raw={'prompt_tokens': 767, 'total_tokens': 774, 'completion_tokens': 7}), raw={'id': '01m1x93eb4s5c3vxrsmyf7bmny', 'object': 'chat.completion', 'created': 1788762766, 'model': 'vlx-seek-1.5-3b', 'choices': [{'index': 0, 'message': {'role': 'assistant', 'content': '<ground>火</ground><objects>None</objects>', 'reasoning_content': ''}, 'logprobs': {}, 'finish_reason': 'stop', 'result_bbox_list': []}], 'usage': {'prompt_tokens': 767, 'total_tokens': 774, 'completion_tokens': 7}})
"""