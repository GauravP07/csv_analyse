from django.shortcuts import render
import pandas as pd
from .forms import UploadCSVForm
from django.core.files.storage import FileSystemStorage

# Create your views here.

def upload_file(request):
    if request.method == 'POST':
        form= UploadCSVForm(request.POST,request.FILES)
        if form.is_valid():
            file= request.FILES['file']
            fs=FileSystemStorage()
            filename=fs.save(file.name,file)
            file_url=fs.url(filename)
            data= pd.read_csv(fs.path(filename))


            head= data.head().to_html()
            summary=data.describe().to_html()
            missing=data.isnull().sum().to_html()
            

            plots=[]

            for column in data.select_dtypes(include=['float64','int64']).columns:
                plot = data[column].plot(kind='hist').get_figure()
                plot.savefig(f'static/{column}.png')
                plots.append(f'{column}.png')
                plot.clear()
            
            return render(request,'analyse/result.html',{'head':head,'summary':summary,'missing':missing,'plots':plots,})
    
    else:
        form=UploadCSVForm()
    return render(request, 'analyse/upload.html',{'form':form})