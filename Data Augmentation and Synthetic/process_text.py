import re

# Templates
template1 = """Hướng dẫn: Bạn có vai trò là một người synthetic data cho người dùng. Người dùng sẽ đưa vào thông tin về bệnh lý nhiệm vụ của bạn là sinh ra dữ liệu hội thoại bao gồm {} đoạn giữa Bác sĩ AI và người dùng.
Lưu ý: Mỗi đoạn hội thoại được bắt đầu bằng [START] và kết thúc là [END], không cần markdown
Ví dụ mẫu:
[START]Người dùng: Chào và hỏi gì đó...
Bác sĩ AI: Trả lời gì đó...
Người dùng: hỏi tiếp gì đó...
Bác sĩ AI: Trả lời gì đó...
Người dùng: hỏi tiếp gì đó...
Bác sĩ AI: Trả lời gì đó[END]
[START]Người dùng: Chào và hỏi gì đó...
Bác sĩ AI: Trả lời gì đó...
Người dùng: hỏi tiếp gì đó...
Bác sĩ AI: Trả lời gì đó...
Người dùng: hỏi tiếp gì đó...
Bác sĩ AI: Trả lời gì đó[END]
Tiếp tục đến khi đủ số lượng yêu cầu!

Nội dung người dùng cung cấp như sau: {}"""

def synthetic_data_generation_template(number, context):
    return template1.format(number, context)

template2 = """Hướng dẫn: Bạn có vai trò tăng cường dữ liệu văn bản cho người dùng. Người dùng sẽ đưa vào thông tin về bệnh lý và nhiệm vụ của bạn là trình bày lại đoạn văn bản đó {} lần nhưng đa dạng cách trình bày.
Lưu ý: Mỗi đoạn văn bản đều được bắt đầu bằng [START] và kết thúc là [END] trong đó không có ký tự xuống hàng, không cần markdown, trình bày càng dài càng đủ ý càng tốt.
Ví dụ mẫu: người dùng đưa vào thông tin bệnh sốt
[START]Sốt là hiện tượng...[END]
[START]Hiện tượng mà ... là sốt[END]
[START]Nguyên nhân của sốt là...[END]
[START]Cách điều trị của sốt là...[END]
[START]Biến chứng ... [END]
[START]Cách phòng bệnh ... [END]
Tiếp tục trình bày đến khi đủ số lượng yêu cầu!

Nội dung người dùng cung cấp như sau: {}"""
def data_augmentation_template(number, context):
    return template2.format(number, context)

template3 = """Hướng dẫn: Bạn có vai trò tăng cường dữ liệu văn bản cho người dùng. Người dùng sẽ đưa vào thông tin về bệnh lý và nhiệm vụ của bạn là trình bày lại đoạn văn bản đó {} lần nhưng đa dạng cách trình bày với phong cách bác sĩ tư vấn cho người dùng.
Lưu ý: Mỗi đoạn văn bản đều được bắt đầu bằng [START] và kết thúc là [END] trong đó không có ký tự xuống hàng, không cần markdown, trình bày càng dài càng đủ ý càng tốt.
Ví dụ mẫu: người dùng đưa vào thông tin bệnh sốt
[START]Bạn có biết sốt là hiện tượng...[END]
[START]Hiện tượng mà ... đó là dấu hiện bạn biết là sốt[END]
[START]Nguyên nhân của sốt là... tôi khuyên bạn nên ...[END]
[START]Cách điều trị của sốt là... đến bệnh viện gần nhất hoặc đến gặp tôi nhé![END]
[START]Biến chứng ... Rất nguy hiểm bạn cần chú ý![END]
[START]Cách phòng bệnh ... Bạn nhớ nhé![END]
Tiếp tục trình bày đến khi đủ số lượng yêu cầu!

Nội dung người dùng cung cấp như sau: {}"""
def data_augmentation_template2(number, context):
    return template3.format(number, context)

template4 = """Hướng dẫn: Bạn có vai trò là text editor dữ liệu văn bản cho người dùng. Người dùng sẽ đưa vào một đoạn văn bản (có thể gồm 1 hoặc nhiều nội dung). Nhiệm vụ của bạn là trình bày lại các nội dung đó cho đúng nếu nó sai chính tả hoặc trình bày không rành mạch.
Lưu ý: Mỗi đoạn văn bản đều được bắt đầu bằng [START] và kết thúc là [END] trong đó không có ký tự xuống hàng, không cần markdown
Ví dụ mẫu: người dùng đưa vào đoạn văn bản có thông tin là khái niệm và nguyên nhân bệnh Chốc
[START]Khái niệm bệnh Chốc...[END]
[START]Nguyên nhân bệnh chốc...[END]
Tiếp tục trình bày nếu còn nội dung khác

Nội dung người dùng cung cấp như sau: {}"""

def text_editor_template(context):
    return template4.format(context)

# clear response function
def clear_response(response):
    # Thay thế \n\n bằng \n
    response = re.sub(r'\n\n+', '\n', response)
    
    # Loại bỏ markdown như ** và *
    response = re.sub(r'\*\*|\*', '', response)
    
    return response

# extract text in response [START]...[END]
def extract_response(response):
    # Sử dụng regex để tìm tất cả các chuỗi nằm giữa [START] và [END]
    pattern = r'\[START\](.*?)\[END\]'
    conversations = re.findall(pattern, response, re.DOTALL)  # re.DOTALL để match cả xuống dòng

    # Loại bỏ các khoảng trắng thừa đầu và cuối chuỗi
    conversations = [conv.strip() for conv in conversations]
    
    return conversations