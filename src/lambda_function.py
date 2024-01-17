from datetime import datetime
import os
import boto3
import cv2
from urllib.parse import unquote_plus
from PIL import Image
import numpy as np
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen.canvas import Canvas
from pdf2image import convert_from_path, convert_from_bytes
import subprocess

s3          = boto3.client('s3')
bucket_name = 'itdose-dev'
dirPrefix   = '/tmp/'
newFile     = ''
# custom_lib_path = dirPrefix + 'libraries'
# sys.path.append(custom_lib_path)

def list_files(directory):
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    # Print the list of files
    for file in files:
        print('local files that exists in tmp:', file)

def remove_logo(input_image_path, output_image_path, logo_template_path):

    image   = cv2.imread(input_image_path)
    ret     = 0
    for logo_temp in logo_template_path:
        logo_template = cv2.imread(logo_temp, cv2.IMREAD_COLOR)
        # Convert the images to grayscale
        gray_image  = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray_logo   = cv2.cvtColor(logo_template, cv2.COLOR_BGR2GRAY)
        # Use template matching to find the logo in the image
        result = cv2.matchTemplate(gray_image, gray_logo, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        threshold = 0.6
        if max_val >= threshold:
            h, w         = gray_logo.shape
            top_left     = max_loc
            bottom_right = (top_left[0] + w, top_left[1] + h)
            # Create a mask for the logo region
            mask = np.zeros_like(gray_image, dtype=np.uint8)
            mask[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]] = 255
            # Use inpainting to fill the logo region with nearby image content
            inpainted_image = cv2.inpaint(image, mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)
            # Save the output image
            cv2.imwrite(output_image_path, inpainted_image)
            print("Logo removed successfully.")
            ret+=1
        else:
            print("Logo not found in the image.")    
    return ret

# exit()
def last_4chars(x):
    return(x[-7:])

def processPdf():
    folder_path         = dirPrefix
    image_extensions    = ['.jpeg']
    image_paths         = []
    directory           = 'reportsImageToRemove/'
    local_download_path = dirPrefix
    resp                = s3.list_objects(Bucket=bucket_name, Prefix=directory)
    logo_template_path  = []
    for obj in resp.get('Contents', []):
        imgPath = os.path.join(local_download_path, os.path.basename(obj['Key']))
        print('bucket_name: ', bucket_name)
        print('object: ', obj['Key'])
        print('imgPath: ', imgPath)
        s3.download_file(bucket_name, obj['Key'], imgPath)
        print(f"Downloaded to: {imgPath}")
        logo_template_path.append(imgPath)

    for filename in sorted(os.listdir(folder_path), key = last_4chars):    
        if any(filename.lower().endswith(ext) for ext in image_extensions):
            file_path = os.path.join(folder_path, filename)
            image_paths.append(file_path)

    for image_path in image_paths:
        k = remove_logo(image_path, image_path, logo_template_path)
        if(k == 1):
            continue
        print(k)
        max = 0
        while(k and max < 10):
            k = remove_logo(image_path, image_path, logo_template_path)
            max += 1
            
    global newFile
    output_pdf = dirPrefix + newFile
    print("Output PDF is at line 155 - above convert_images_to_pdf: ", output_pdf)
    convert_images_to_pdf(image_paths, output_pdf)
    for image_path in image_paths:
        os.remove(image_path)
    # for nabl in logo_template_path:
    #     os.remove(nabl)    
    print(f"Images converted to PDF and combined into '{output_pdf}'.")
    s3_key = 'uploads/modifiedReports/' + newFile
    # Upload the file to S3
    s3.upload_file(output_pdf, bucket_name, s3_key)
    os.remove(output_pdf)
    print(f"File uploaded to S3. Bucket: {bucket_name}, Key: {s3_key}")  


def convert_images_to_pdf(image_paths, output_pdf_path):
    pdf_width, pdf_height   = A4
    pdf_canvas              = Canvas(output_pdf_path, pagesize=A4)
    for image_path in image_paths:
        pdf_canvas.drawInlineImage(image_path, 0,0,pdf_width,pdf_height,True)
        pdf_canvas.showPage()
    pdf_canvas.save()

def read_pdf(file_name):
    try:
        print('func read_pdf() - var file_name: ', file_name)
        # with tempfile.TemporaryDirectory() as path:
        #     images = convert_from_path(file_name, output_folder=path)
        # images = convert_from_path(file_name)
        images = convert_from_path(file_name, poppler_path='/opt/poppler/bin')
        for i, image in enumerate(images):
            filename = dirPrefix + "image_" + str(i) + ".jpeg"
            image.save(filename, "JPEG")
            im = Image.open(filename)
            width, height   = im.size
            new_width       = width
            new_height      = height
            new_image       = Image.new("RGB", (new_width, new_height), "white")
            x_position      = 0
            y_position      = 0
            new_image.paste(im, (x_position, y_position))        
            new_image.save(filename, "JPEG")
            im.close()
        processPdf()
        # os.remove(file_name)
    except Exception as e:
        print('func: read_pdf - Exception: ', e)
        raise e
    
def lambda_handler(event, context):
    print('starting lambda handler execution ', datetime.now())
    # print("Received event: " + json.dumps(event, indent=2))
    # Get the object from the event and show its content type
    # download_and_import_libraries(bucket_name, 'python-lib/py-package.zip', custom_lib_path)
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    print("Bucket: " + bucket_name)
    key = unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    fileName = os.path.basename(key)
    print("File name: " + key)
    global newFile    
    try:
        response = s3.get_object(Bucket=bucket_name, Key=key)
        print("CONTENT TYPE: ", response['ContentType'])
        pdf_file = os.path.join(dirPrefix, fileName)
        s3.download_file(bucket_name, key, pdf_file)
        print('environment path: ', os.environ['PATH'])
        # os.environ['PATH'] = '/usr/bin:' + '/var/task/bin:' + os.environ['PATH']
        print('environment path: ', os.environ['PATH'])
        # subprocess.run(['pdftotext', '-v'])
        newFile = fileName
        print(f"Downloaded to: {pdf_file}")
        list_files(dirPrefix)
        list_files('/var/task/')        
        read_pdf(pdf_file)
        # os.remove(pdf_file)        
        return response['ContentType']
    except Exception as e:
        print('func: lambda_handler - Exception: ', e)
        # print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket_name))
        raise e