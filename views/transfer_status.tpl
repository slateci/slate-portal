%include('views/header.tpl')

<div class="container">

	<div class="page-header">
		<h1>Transfer Status</h1>
	</div>

  %if not transfer_status:
  
  <p>Transfer request submitted successfully. Task ID: {{ task_id }}</p>
  
  %else:
  
  <p><strong>Task ID</strong>: {{ task_id }}</p>
  <p><strong>Source endpoint</strong>: {{ transfer_status['source_ep_name'] }}</p>
  <p><strong>Destination Endpoint</strong>: {{ transfer_status['dest_ep_name'] }}</p>
  <p><strong>Request Time</strong>: {{ transfer_status['request_time'] }}</p>
  <p><strong>Status</strong>: {{ transfer_status['status'] }}</p>
  <p><strong>Files transferred</strong>: {{ transfer_status['files_transferred'] }}</p>
  <p><strong>Faults</strong>: {{ transfer_status['faults'] }}</p>

  %end
	
	<div class="form-wrapper">
	  <form role="form" action="{{get_url('transfer_status', task_id=task_id) }}" method="post">

	    <div class="form-actions">
	      <input class="btn btn-lg btn-primary" type="submit" value="Refresh" />&nbsp;&nbsp;&nbsp;
	    </div>
	  </form>
   </div> <!-- form -->

</div> <!-- container -->

%rebase('views/base', title='MDRP - Transfer Status')
