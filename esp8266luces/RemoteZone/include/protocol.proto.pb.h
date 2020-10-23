/* Automatically generated nanopb header */
/* Generated by nanopb-0.4.2 */

#ifndef PB_PROTOCOL_PROTO_PB_H_INCLUDED
#define PB_PROTOCOL_PROTO_PB_H_INCLUDED
#include <pb.h>

#if PB_PROTO_HEADER_VERSION != 40
#error Regenerate this file with the current version of nanopb generator.
#endif

#ifdef __cplusplus
extern "C" {
#endif

/* Struct definitions */
typedef struct _SimpleMessage {
    int32_t Pin;
    int32_t RGBint;
    bool End;
} SimpleMessage;


/* Initializer values for message structs */
#define SimpleMessage_init_default               {0, 0, 0}
#define SimpleMessage_init_zero                  {0, 0, 0}

/* Field tags (for use in manual encoding/decoding) */
#define SimpleMessage_Pin_tag                    1
#define SimpleMessage_RGBint_tag                 2
#define SimpleMessage_End_tag                    3

/* Struct field encoding specification for nanopb */
#define SimpleMessage_FIELDLIST(X, a) \
X(a, STATIC,   REQUIRED, INT32,    Pin,               1) \
X(a, STATIC,   REQUIRED, INT32,    RGBint,            2) \
X(a, STATIC,   REQUIRED, BOOL,     End,               3)
#define SimpleMessage_CALLBACK NULL
#define SimpleMessage_DEFAULT NULL

extern const pb_msgdesc_t SimpleMessage_msg;

/* Defines for backwards compatibility with code written before nanopb-0.4.0 */
#define SimpleMessage_fields &SimpleMessage_msg

/* Maximum encoded size of messages (where known) */
#define SimpleMessage_size                       24

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif
