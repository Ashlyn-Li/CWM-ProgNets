/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>


 /*        0                1                  2              3
 * +----------------+----------------+----------------+---------------+
 * |      P         |       4        |     Version    |     Op        |
 * +----------------+----------------+----------------+---------------+
 * |                                Hand                              |
 * +----------------+----------------+----------------+---------------+
 * |                                Ace                               |
 * +----------------+----------------+----------------+---------------+
 * |                               Result                             |
 
 
/*************************************************************************
*********************** H E A D E R S  ***********************************
*************************************************************************/

typedef bit<9>  egressSpec_t;
typedef bit<48> macAddr_t;

header ethernet_t {
    macAddr_t dstAddr;
    macAddr_t srcAddr;
    bit<16>   etherType;
}

/* this is a custom protocol header for the blackjack game/
*/

const bit<16> TYPE_BLACK = 0x1234;

header black_t {
	
	bit<8> p;
    bit<8> four;
    bit<8> ver;
    bit<8>  op;
	bit<32> hand;
	bit<32> ace;
	bit<32> result;
}

struct metadata {
    /* empty */
}

struct headers {
    ethernet_t   ethernet;
    black_t    black;
}

/*************************************************************************
*********************** P A R S E R  ***********************************
*************************************************************************/

parser MyParser(packet_in packet,
                out headers hdr,
                inout metadata meta,
                inout standard_metadata_t standard_metadata) {

    state start {
        /* TODO: add parser logic */
        transition parse_ethernet;
    }
    
    state parse_ethernet{
    	packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType){
        	0x1234: parse_black;
        	default: accept;
        	}
        	
   }
    state parse_black{
    	packet.extract(hdr.black);
        transition accept;
    }
}


/*************************************************************************
************   C H E C K S U M    V E R I F I C A T I O N   *************
*************************************************************************/

control MyVerifyChecksum(inout headers hdr, inout metadata meta) {
    apply {  }
}


/*************************************************************************
**************  I N G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyIngress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {

    action send_back() {
        /* Send back the result*/
        bit<48> temp_Mac; 
        temp_Mac = hdr.ethernet.srcAddr;
        hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;
        hdr.ethernet.dstAddr = temp_Mac;       
        standard_metadata.egress_spec = standard_metadata.ingress_port;       
        
    }
    
    action hit_or_stand(){
    	/*if the hand card value is greater than 17 than stand, otherwise hit*/
    	if (hdr.black.hand > 17 && hdr.black.ace == 0){
    		hdr.black.result = 0 ;
    		send_back(); 
    	}else {
    		hdr.black.result = 1;
    		send_back(); 
    		}    	
    }
    
    action operation_drop() {
        mark_to_drop(standard_metadata);
    }

    table blackjack {
    	key={
    		hdr.black.p:   exact;
    	}
        actions = {
            hit_or_stand;
            operation_drop;
            NoAction;
        }
        size = 1024;
        const default_action = hit_or_stand();
    }

    apply {
        /* TODO: Apply the action when reuqired
         */
        if (hdr.black.isValid()){
        	blackjack.apply();
        }
    }
}

/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {
    apply {  }
}

/*************************************************************************
*************   C H E C K S U M    C O M P U T A T I O N   **************
*************************************************************************/

control MyComputeChecksum(inout headers hdr, inout metadata meta) {
     apply {}
}


/*************************************************************************
***********************  D E P A R S E R  *******************************
*************************************************************************/

control MyDeparser(packet_out packet, in headers hdr) {
    apply {
        /* TODO: add deparser logic */
        packet.emit(hdr.ethernet);
        packet.emit(hdr.black);
    }
}

/*************************************************************************
***********************  S W I T C H  *******************************
*************************************************************************/

V1Switch(
MyParser(),
MyVerifyChecksum(),
MyIngress(),
MyEgress(),
MyComputeChecksum(),
MyDeparser()
) main;
