from django.shortcuts import render
import pandas as pd
from .forms import UploadCSVForm
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponseBadRequest
import os

def upload_file(request):
    if request.method == 'POST':
        form = UploadCSVForm(request.POST, request.FILES)
        if form.is_valid():
            if 'file' not in request.FILES:
                return HttpResponseBadRequest("File not found in the request.")
            
            file = request.FILES['file']
            fs = FileSystemStorage()
            filename = fs.save(file.name, file)
            file_url = fs.url(filename)
            data = pd.read_csv(fs.path(filename))

            # Perform basic data analysis
            head = data.head().to_html()
            summary = data.describe().to_html()
            missing = data.isnull().sum().reset_index().to_html(header=["Column", "Missing Values"], index=False)

            # Ensure the static directory exists
            static_dir = os.path.join('static')
            if not os.path.exists(static_dir):
                os.makedirs(static_dir)

            # Visualizations
            plots = []

            for column in data.select_dtypes(include=['float64', 'int64']).columns:
                plot = data[column].plot(kind='hist').get_figure()
                plot_path = os.path.join(static_dir, f'{column}.png')
                plot.savefig(plot_path)
                plots.append(f'{column}.png')
                plot.clear()

            return render(request, 'analyse/result.html', {
                'head': head,
                'summary': summary,
                'missing': missing,
                'plots': plots,
            })
    else:
        form = UploadCSVForm()
    return render(request, 'analyse/upload.html', {'form': form})
