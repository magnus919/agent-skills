`timescale 1ns/1ps
module tb_rv_buffer;
    parameter integer DATA_WIDTH = 8;
    reg clk = 0, rst = 1, in_valid = 0, out_ready = 0;
    reg [DATA_WIDTH-1:0] in_data = 0;
    wire in_ready, out_valid;
    wire [DATA_WIDTH-1:0] out_data;
    integer seed = 20260914, i, errors = 0;
    reg model_full;
    reg [DATA_WIDTH-1:0] model_data;
    reg [DATA_WIDTH-1:0] next_data;
    reg held_valid;
    reg [DATA_WIDTH-1:0] held_data;
    integer accepted_in = 0, accepted_out = 0, stalled = 0, simultaneous = 0, reset_occupied = 0;

    rv_buffer #(.DATA_WIDTH(DATA_WIDTH)) dut (.*);
    always #5 clk = ~clk;

    task automatic check_visible;
        begin
            if (out_valid !== model_full) begin
                $display("ERROR visible valid got=%b want=%b t=%0t", out_valid, model_full, $time); errors = errors + 1;
            end
            if (model_full && out_data !== model_data) begin
                $display("ERROR visible data got=%h want=%h t=%0t", out_data, model_data, $time); errors = errors + 1;
            end
            if (in_ready !== (~model_full | out_ready)) begin
                $display("ERROR ready got=%b want=%b t=%0t", in_ready, (~model_full | out_ready), $time); errors = errors + 1;
            end
        end
    endtask

    task automatic cycle(input reg v, input reg [DATA_WIDTH-1:0] d, input reg r);
        reg accept_in, accept_out;
        begin
            if (held_valid) begin v = 1'b1; d = held_data; end
            @(negedge clk); in_valid = v; in_data = d; out_ready = r; #1; check_visible();
            accept_out = model_full && r;
            accept_in = v && (~model_full | r);
            if (v && !in_ready) begin held_valid = 1'b1; held_data = d; stalled = stalled + 1; end
            else held_valid = 1'b0;
            if (accept_in) accepted_in = accepted_in + 1;
            if (accept_out) accepted_out = accepted_out + 1;
            if (accept_in && accept_out) simultaneous = simultaneous + 1;
            if (rst && model_full) reset_occupied = reset_occupied + 1;
            @(posedge clk); #1;
            if (rst) begin model_full = 1'b0; model_data = 0; end
            else if (accept_in) begin model_full = 1'b1; model_data = d; end
            else if (accept_out) model_full = 1'b0;
            check_visible();
        end
    endtask

    initial begin
        if (!$value$plusargs("SEED=%d", seed)) seed = 20260914;
        model_full = 0; model_data = 0;
        held_valid = 0; held_data = 0;
        repeat (2) cycle(0, 0, 0);
        rst = 0;
        cycle(1, {DATA_WIDTH{1'b0}}, 0);
        cycle(1, {DATA_WIDTH{1'b1}}, 0);
        cycle(0, 0, 1);
        cycle(1, {DATA_WIDTH{1'b1}}, 1);
        cycle(1, {DATA_WIDTH{1'b0}}, 1);
        cycle(1, {DATA_WIDTH{1'b1}}, 0);
        cycle(0, 0, 0);
        cycle(1, {DATA_WIDTH{1'b0}}, 0); cycle(0, 0, 0); cycle(0, 0, 0); cycle(0, 0, 0);
        cycle(0, 0, 1);
        rst = 1; cycle(1, {DATA_WIDTH{1'b1}}, 0); rst = 0;
        for (i = 0; i < 300; i = i + 1) begin
            next_data = $urandom(seed);
            cycle($urandom(seed) & 1, next_data, $urandom(seed) & 1);
            if (i == 127) begin rst = 1; cycle(1, next_data, 0); rst = 0; end
        end
        cycle(0, 0, 1); cycle(0, 0, 1);
        if (accepted_in == 0 || accepted_out == 0 || stalled == 0 || simultaneous == 0 || reset_occupied == 0) begin
            $display("FAIL width=%0d missing scenario counts in=%0d out=%0d stall=%0d simultaneous=%0d reset_occupied=%0d", DATA_WIDTH, accepted_in, accepted_out, stalled, simultaneous, reset_occupied);
            $fatal(1);
        end
        if (errors == 0) $display("PASS width=%0d seed=%0d in=%0d out=%0d stall=%0d simultaneous=%0d reset_occupied=%0d", DATA_WIDTH, seed, accepted_in, accepted_out, stalled, simultaneous, reset_occupied);
        else begin $display("FAIL width=%0d errors=%0d", DATA_WIDTH, errors); $fatal(1); end
        $finish;
    end
endmodule
