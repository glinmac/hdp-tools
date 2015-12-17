# Ambari Notes

## Widgets

This can be achieved using the widget editor in the UI or also could be automated using the Ambari API.

### Create

Widgets are defined in JSON, for instance for details about the NameNode heap:

    {  
      "WidgetInfo" : {
        "author" : "admin",
        "cluster_name" : "hadoop_cluster",
        "widget_name" : "NameNode Heap (COPY of Existing)",
        "description" : "Heap memory committed and Heap memory used with respect to time.",    
        "metrics" : [{"service_name":"HDFS","component_name":"NAMENODE","name":"jvm.JvmMetrics.MemHeapUsedM._avg","metric_path":"metrics/jvm/memHeapUsedM._avg"},{"service_name":"HDFS","component_name":"NAMENODE","name":"jvm.JvmMetrics.MemHeapCommittedM._avg","metric_path":"metrics/jvm/memHeapCommittedM._avg"}],
        "properties" : {"graph_type":"LINE","display_unit":"MB"},
        "scope" : "USER",    
        "values" : [{"name":"jvm.JvmMetrics.MemHeapUsedM","value":"${jvm.JvmMetrics.MemHeapUsedM._avg}"},{"name":"jvm.JvmMetrics.MemHeapCommittedM","value":"${jvm.JvmMetrics.MemHeapCommittedM._avg}"}],
        "widget_type" : "GRAPH"
      }
    }
    
This can be sent to the widget endpoint:
    
    $ curl -u admin:admin -H 'X-Requested-By: ambari' -i \
       -X POST \
       -d @widget.json
       http://localhost:8080/api/v1/clusters/hadoop_cluster/widgets
    
    HTTP/1.1 201 Created
    ...
    {
      "resources" : [
        {
          "href" : "http://localhost:8080/api/v1/clusters/hadoop_cluster/widgets/252",
          "WidgetInfo" : {
            "id" : 252
          }
        }
      ]
    }

### Retrieve / Get

You can then check that it is defined: 

* All widgets: http://localhost:8080/api/v1/clusters/hadoop_cluster/widgets
* Widget just created: http://localhost:8080/api/v1/clusters/hadoop_cluster/widgets/252
    
### Update

Same process than creation but with a PUT request with the new widget definition:

    $ curl -u admin:admin -H 'X-Requested-By: ambari' -i \
           -X PUT \
           -d @widget.json
           http://localhost:8080/api/v1/clusters/hadoop_cluster/widgets/252

### Delete

This can be deleted by sending a DELETE request:

    $ curl -u admin:admin -H 'X-Requested-By: ambari' -i \
           -X DELETE \
           http://localhost:8080/api/v1/clusters/hadoop_cluster/widgets

### Mapping a widget to a widget layout

User can map manually widget to their prefered dashboard or this could also be automated so that it is available by default.

The following gives the list of layouts available:

    $ curl -u admin:admin -H 'X-Requested-By: ambari' -i  \
        http://localhost:8080/api/v1/clusters/hadoop_cluster/widget_layouts
    HTTP/1.1 200 OK
    ...
    {
      "href" : "http://localhost:8080/api/v1/clusters/hadoop_cluster/widget_layouts",
      "items" : [
        {
          "href" : "http://localhost:8080/api/v1/clusters/hadoop_cluster/widget_layouts/8",
          "WidgetLayoutInfo" : {
            "cluster_name" : "hadoop_cluster",
            "display_name" : "Standard HDFS Dashboard",
            "id" : 8,
            "layout_name" : "admin_hdfs_dashboard",
            "scope" : "USER",
            "section_name" : "HDFS_SUMMARY",
            "user_name" : "admin",
            "widgets" : [
              {
                "href" : "http://localhost:8080/api/v1/clusters/hadoop_cluster/widgets/20",
                "WidgetInfo" : {
                  "id" : 20,
    ...
    
You can also use a filter to look for a specific widget given one of its property:

    $ curl -u admin:admin -H 'X-Requested-By: ambari' -i  \
        http://localhost:8080/api/v1/clusters/hadoop_cluster/widget_layouts?WidgetLayoutInfo/layout_name=admin_hdfs_dashboard

To add a widget to a given layout, this is a matter of updating the list of widget IDs associated with the widget layout.

The data to update:

    {
      "WidgetLayoutInfo":
    	{
    		"display_name":"Standard HDFS Dashboard",
    		"id":8,
    		"layout_name":"admin_hdfs_dashboard",
    		"scope":"USER",
    		"section_name":"HDFS_SUMMARY",
    		"widgets":
    			[{"id":20},{"id":23},{"id":22},{"id":24},{"id":21},{"id":153},{"id":152},{"id":25},{"id":26},{"id":27},{"id":28},{"id":29},{"id":252}]
    	}
    }

The update request:

    $ curl -u admin:admin -H 'X-Requested-By: ambari' -i  \
        -X PUT \
        -d @widget_layout.json \
        http://localhost:8080/api/v1/clusters/hadoop_cluster/widget_layouts/8
