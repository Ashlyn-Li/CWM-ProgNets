/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>


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

header black_t {
	
	bit<8> hand;
	bit<8> res;
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
        transition parse_black;
        	
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
    action drop() {
        mark_to_drop(standard_metadata);
    }

    action send_back(bit<8> result) {
        /* Send back the result*/
        bit<48> temp_Mac; 
        hdr.black.res = result;
        temp_Mac = hdr.ethernet.srcAddr;
        hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;
        hdr.ethernet.dstAddr = temp_Mac;
        
        standard_metadata.egress_spec = standard_metadata.ingress_port;       
        
    }
    
    action hit_or_stand(){
    	/*if the hand card value is greater than 17 than stand, otherwise hit*/
    	bit<8> result
    	if hdr.black.hand > 17{
    		result = 0 ;/*This stands for a stand action*/
    		}
    	else hdr.black.hand <= 17{
    		result = 1 ;/*This stands for a hit action*/
    	send_back(result);
    }

    table blackjack {
        key = {
            hdr.black.hand: exact;
        }
        actions = {
            hit_or_stand;
            drop;
            NoAction;
        }
        size = 1024;
        default_action = hit_or_stand;
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
