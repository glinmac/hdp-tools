""" quick configuration values
"""

ambari_host = 'localhost'
ambari_port = 8080
ambari_user = 'admin'
ambari_password = 'admin'
cluster_name = 'hadoop_cluster'
ambari_api = '/api/v1/clusters/%s' % cluster_name
widget_layout = 'admin_hdfs_dashboard'

new_widgets = {
	'NameNode GC count': {
		"WidgetInfo" : {
			"author" : "admin",
			"cluster_name" : cluster_name,
			"description" : "Count of total garbage collections and count of major type garbage collections of the JVM.",
			"metrics" : [{"service_name":"HDFS","component_name":"NAMENODE","name":"jvm.JvmMetrics.GcCount._avg","metric_path":"metrics/jvm/gcCount._avg"},{"service_name":"HDFS","component_name":"NAMENODE","name":"jvm.JvmMetrics.GcCountConcurrentMarkSweep._avg","metric_path":"metrics/jvm/JvmMetrics/GcCountConcurrentMarkSweep._avg"}],
			"properties" : {"graph_type":"LINE","display_unit":""},
			"scope" : "USER",
			"values" : [{"name":"GC total count","value":"${jvm.JvmMetrics.GcCount._avg}"},{"name":"GC count of type major collection","value":"${jvm.JvmMetrics.GcCountConcurrentMarkSweep._avg}"}],
			"widget_name" : "NameNode GC count (NEW VERSION)",
			"widget_type" : "GRAPH"
		}
	},

	'NameNode Host Load': {
	  "WidgetInfo" : {
	    "author" : "admin",
	    "cluster_name" : cluster_name,
	    "description" : "Percentage of CPU and Memory resources being consumed on NameNode host.",
	    "metrics" : [{"service_name":"HDFS","component_name":"NAMENODE","name":"cpu_system._avg","metric_path":"metrics/cpu/cpu_system._avg"},{"service_name":"HDFS","component_name":"NAMENODE","name":"cpu_user._avg","metric_path":"metrics/cpu/cpu_user._avg"},{"service_name":"HDFS","component_name":"NAMENODE","name":"cpu_nice._avg","metric_path":"metrics/cpu/cpu_nice._avg"},{"service_name":"HDFS","component_name":"NAMENODE","name":"cpu_idle._avg","metric_path":"metrics/cpu/cpu_idle._avg"},{"service_name":"HDFS","component_name":"NAMENODE","name":"cpu_wio._avg","metric_path":"metrics/cpu/cpu_wio._avg"},{"service_name":"HDFS","component_name":"NAMENODE","name":"mem_total._avg","metric_path":"metrics/memory/mem_total._avg"},{"service_name":"HDFS","component_name":"NAMENODE","name":"mem_free._avg","metric_path":"metrics/memory/mem_free._avg"},{"service_name":"HDFS","component_name":"NAMENODE","name":"mem_cached._avg","metric_path":"metrics/memory/mem_cached._avg"}],
	    "properties" : {"graph_type":"LINE","display_unit":"%"},
	    "scope" : "USER",
	    "values" : [{"name":"CPU utilization","value":"${((cpu_system._avg+cpu_user._avg+cpu_nice._avg)/(cpu_system._avg+cpu_nice._avg+cpu_user._avg+cpu_idle._avg+cpu_wio._avg))*100}"},{"name":"Memory utilization","value":"${((mem_total._avg-mem_free._avg-mem_cached._avg)/mem_total._avg)*100}"}],
	    "widget_name" : "NameNode Host Load (NEW VERSION)",
	    "widget_type" : "GRAPH"
	  }
	}
}
