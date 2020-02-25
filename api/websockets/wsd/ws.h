#define WS_PING_TIMEOUT 10
#define WS_TIMEOUT 120 // 2 minutes for authorize
#define WS_FIN 0x80
#define WS_OPCODE 0x0f
#define WS_MASKED 0x80
#define WS_PAYLOAD_LEN 0x7f
#define WS_PAYLOAD_LEN16 0x7e
#define WS_PAYLOAD_LEN64 0x7f

#define WS_CONTINUATION_FRAME 0x00
#define WS_TEXT_FRAME 0x01
#define WS_BINARY_FRAME 0x02
#define WS_PING_FRAME 0x09
#define WS_PONG_FRAME 0x0A
#define WS_CLOSING_FRAME 0x08

#define SW_BUF 65552
#define WS_WRONG_MESSAGE "WRONG WobSocket message!"

char response[] = "HTTP/1.1 200 OK\r\n"
"Content-Type: text/html; charset=UTF-8\r\n\r\n";

char response_404[] = "HTTP/1.1 404 Not Found\r\n"
"Content-Type: text/html; charset=UTF-8\r\n\r\n";

char response_500[] = "HTTP/1.1 500 Internal Server Error\r\n"
"Content-Type: text/html; charset=UTF-8\r\n\r\n";

char response_img[] = "HTTP/1.1 200 OK\r\n"
"Content-Type: image/png; charset=UTF-8\r\n\r\n";

char response_xicon[] = "HTTP/1.1 200 OK\r\n"
"Content-Type: image/x-icon; charset=UTF-8\r\n\r\n";

char response_css[] = "HTTP/1.1 200 OK\r\n"
"Content-Type: text/css; charset=UTF-8\r\n\r\n";

char response_js[] = "HTTP/1.1 200 OK\r\n"
"Content-Type: text/js; charset=UTF-8\r\n\r\n";

char response_ttf[] = "HTTP/1.1 200 OK\r\n"
"Content-Type: font/ttf ; charset=UTF-8\r\n\r\n";

char response_text[] = "HTTP/1.1 200 OK\r\n"
"Content-Type: text/text; charset=UTF-8\r\n\r\n";

char response_403[] = "HTTP/1.1 200 OK\r\n"
"Content-Type: text/html; charset=UTF-8\r\n\r\n"
"<!DOCTYPE html><html><head><title>403</title>"
"<style>body { background-color: #312f2f }"
"h1 { font-size:4cm; text-align: center; color: #666;}</style></head>"
"<body><h1>403</h1></body></html>\r\n";

char GUIDKey[] = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"; //36

char response_ws[] = "HTTP/1.1 101 Switching Protocols\r\n"
"Upgrade: websocket\r\n"
"Connection: Upgrade\r\n"
"Content-Encoding: identity\r\n"
"Sec-WebSocket-Accept: "; //97

