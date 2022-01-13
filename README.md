# Storage Optimizer #

Identify potintial optimizations on the cloud storage accounts (duplicates, compression, clustering ...)

### References ###

* [Files properties](https://developers.google.com/drive/api/v3/reference/files)
* [File format](https://developers.google.com/drive/api/v3/ref-export-formats)
* [List docs](https://developers.google.com/drive/api/v2/reference/files/list)

### Prerequisite ###

* Create [API Project](https://console.cloud.google.com/apis/dashboard)
  ** `auth/drive.metadata` scope for metdata retrieval 
  ** `auth/drive` scrope for delete duplicate files
* Generate [Credentials](https://console.cloud.google.com/apis/credentials) and download `json`
* Enable APIs and Services from [console](https://console.developers.google.com/apis/api/drive.googleapis.com/overview)
