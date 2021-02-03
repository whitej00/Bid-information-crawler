import os
import smtplib
import sqlite3
import datetime
 
from email import encoders
from email.utils import formataddr
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
 
from_addr = formataddr(('Jaker Korea', 'wlsdka12@google.com'))
customers = [
    ["wlsdka12@naver.com",["CABLE", "FUES"]],
]
findSql = """select id, company, documents, Bid_Descriptions, Bid_IssuanceTime, Bid_OpenTime from tender where category like '%{0}%' and  inputTime like '%{1}%'"""
conn = sqlite3.connect("/srv1/process/tender.db")
cur = conn.cursor()

for customer in customers:
    categorys = customer[1]

    # SMTP 세션 생성
    session = smtplib.SMTP('smtp.gmail.com', 587)
    session.set_debuglevel(True)

    # SMTP 계정 인증 설정
    session.ehlo()
    session.starttls()
    session.login('wlsdka12@gmail.com', 'nmekvdqdigxxywqt')

    # 메일 콘텐츠 설정
    message = MIMEMultipart("mixed")

    # 메일 송/수신 옵션 설정
    message.set_charset('utf-8')
    message['From'] = from_addr
    message['To'] = customer[0]
    message['Subject'] = '안녕하세요 제이커 코리아입니다.'

    for category in categorys:
        cur.execute(findSql.format(category, datetime.date.today()))
        items = cur.fetchall()
        for item in items:
            pdfs = item[2].split(',')
            pdfUrl = ""
            for pdf in pdfs:
                pdf = pdf.replace("[apos]", "'")
                pdf = pdf.replace('[quot]', '"')
                pdf = pdf.replace('[comma]',',')
                pdfUrl += '<a href="{0}">{0}</a><br>'.format(pdf)
            body = '''
            <h1>Category : {0} </h1>
            <table>
                <tbody>
                    <tr>
                        <td style="width: 150px;">Company</td><td style="width: auto;">{1}</td>
                    </tr>
                    <tr>
                        <td>PDF FILES</td><td>{2}</td>
                    </tr>
                    <tr>
                        <td>Descriptions</td><td>{3}</td>
                    </tr>
                    <tr>
                        <td>Bid IssuanceTime</td><td>{4}</td>
                    </tr>
                    <tr>
                        <td>Bid OpenTime</td><td>{5}</td>
                    </tr>
                </tbody>
            </table>
            '''.format(category, item[1], pdfUrl, item[3], item[4], item[5])
            bodyPart = MIMEText(body, 'html', 'utf-8')
            message.attach( bodyPart )

        # attachments = [
        #     "C:/Users/wlsdk/process/a1.pdf",
        #     "C:/Users/wlsdk/process/a2.pdf",
        #     "C:/Users/wlsdk/process/a3.pdf",
        #     "C:/Users/wlsdk/process/a4.pdf",
        # ]
        
        # for attachment in attachments:
        #     attach_binary = MIMEBase("application", "octect-stream")
        #     binary = open(attachment, "rb").read() # read file to bytes
        #     attach_binary.set_payload( binary )
        #     encoders.encode_base64( attach_binary ) # Content-Transfer-Encoding: base64
            
        #     filename = os.path.basename( attachment )
        #     attach_binary.add_header("Content-Disposition", 'attachment', filename=('utf-8', '', filename))
            
        #     message.attach( attach_binary )

    # 메일 발송
    session.sendmail(from_addr, customer[0], message.as_string())

    print( 'Successfully sent the mail!!!' )

