from variables import limit_char, limit_length, limit_line
def limit_text(msg):

    if (len(msg) < limit_char) and (len(msg.split(' ')) < limit_length) and (len(msg.split('\n')) < limit_line):
        return False

    if len(msg) >= limit_char:
        msg = ''.join(msg[0:limit_char - 1])

    if len(msg.split(' ')) >= limit_length:
        msg = ' '.join(msg.split(' ')[0:limit_length - 1])

    if len(msg.split('\n')) >= limit_line:
        msg = '\n'.join(msg.split('\n')[0:limit_line - 1])

    return msg