module rv_buffer #(parameter integer DATA_WIDTH = 8) (
    input  wire                  clk,
    input  wire                  rst,
    input  wire                  in_valid,
    output wire                  in_ready,
    input  wire [DATA_WIDTH-1:0] in_data,
    output wire                  out_valid,
    input  wire                  out_ready,
    output wire [DATA_WIDTH-1:0] out_data
);
    reg                  full;
    reg [DATA_WIDTH-1:0] data_reg;

    assign in_ready  = ~full | out_ready;
    assign out_valid = full;
    assign out_data  = data_reg;

    always @(posedge clk) begin
        if (rst) begin
            full     <= 1'b0;
            data_reg <= {DATA_WIDTH{1'b0}};
        end else begin
            case ({in_valid && in_ready, out_valid && out_ready})
                2'b10: begin full <= 1'b1; data_reg <= in_data; end
                2'b01: begin full <= 1'b0; end
                2'b11: begin full <= 1'b1; data_reg <= in_data; end
                default: begin end
            endcase
        end
    end
endmodule
