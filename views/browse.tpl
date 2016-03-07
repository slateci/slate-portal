%include('views/header.tpl')

<div class="container">

	<div class="page-header">
		<h1>Browse Dataset</h1>
	</div>

  <p>Displaying a list of files in dataset <strong>{{ dataset_uri }}</strong>.<br />
  Click on a file name to display the contents in your browser or download via HTTP</p>

  <div class="row">
    <div class="col-md-12">
      <table class="table">
        <th class="col-md-5 text-left">File Name</th><th class="col-md-2 text-right">Size</th>
        %if file_list:
          %for file in file_list:
          <tr>
            <td class="col-md-5 text-left">
              <i class="fa fa-file"></i>&nbsp;
              <a href="http://somehost.edu/{{ file['uri'] }}">{{ file['name'] }}</a>
            </td>
            <td class="col-md-1 text-right">{{ file['size'] }}</td>
          </tr>
          %end
        %else:
        <p>No files found in dataset.</p>
        %end
      </table>
    </div>
  </div>

</div> <!-- container -->

%rebase('views/base', title='MRDP - Browse Dataset')
