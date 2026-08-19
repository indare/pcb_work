#!/usr/bin/env perl
# Run statements on the Pico over CDC, one line at a time, then hand the board
# back to main.py.
#
# Three constraints learned the hard way on this Mac:
#   * Only the first open() after a replug succeeds. A wedged CDC endpoint
#     blocks inside the kernel where SIGALRM cannot reach us, so one open has
#     to do the whole job.
#   * The tty comes up canonical with echo, which returns our own line instead
#     of REPL output. Raw mode is set on the fd we already hold; reopening via
#     stty would burn the one good open.
#   * Paste mode echoes every character back before running anything, and that
#     echo alone can outlast a generous timeout. Sending one statement at a
#     time and waiting for the ">>>" prompt is far more predictable.
#
# Every exit path restarts main.py, otherwise the board sits in a stopped REPL
# and the LCD looks frozen with touch dead.
#
#   perl pico_exec.pl [port] < statements.py
#
use strict;
use warnings;
use POSIX qw(:termios_h);
use Time::HiRes qw(sleep time);

my $port = $ARGV[0] || (glob("/dev/cu.usbmodem*"))[0] || die "no cu.usbmodem\n";
my $src = -t STDIN ? default_code() : do { local $/; <STDIN> };
$src = default_code() unless defined $src && $src =~ /\S/;

my @lines = grep { /\S/ && !/^\s*#/ } split /\r?\n/, $src;
die "no statements\n" unless @lines;
for my $l (@lines) {
    die "statement must be one line, no leading indent: $l\n" if $l =~ /^\s/;
}

my $fh;
my $restored = 0;

sub restore {
    return if $restored || !defined $fh;
    $restored = 1;
    eval {
        local $SIG{ALRM} = sub { die "restore timeout\n" };
        alarm 6;
        syswrite($fh, "\x03");    # cancel paste/continuation
        sleep 0.2;
        syswrite($fh, "\x03");
        sleep 0.2;
        syswrite($fh, "\x04");    # soft reset -> main.py runs again
        sleep 1.5;
        alarm 0;
    };
    print STDERR "RESTORED (soft reset sent, main.py should be running)\n";
}

END { restore() }
$SIG{INT}  = sub { restore(); exit 130 };
$SIG{TERM} = sub { restore(); exit 143 };

print STDERR "PORT $port\n";
$SIG{ALRM} = sub { print STDERR "OPEN_TIMEOUT (replug the Pico USB)\n"; exit 142 };
alarm 3;
open($fh, "+<", $port) or die "open $port: $!\n";
alarm 0;
binmode $fh;
$fh->autoflush(1);

my $fd  = fileno($fh);
my $tio = POSIX::Termios->new;
$tio->getattr($fd);
$tio->setiflag(0);
$tio->setoflag(0);
$tio->setlflag(0);
$tio->setcflag(($tio->getcflag | CLOCAL | CREAD | CS8) & ~(PARENB | CSTOPB));
$tio->setcc(VMIN,  0);
$tio->setcc(VTIME, 0);
$tio->setattr($fd, TCSANOW);
print STDERR "OPEN_OK (raw)\n";

my $rin = "";
vec($rin, $fd, 1) = 1;

sub read_until {
    my ($want, $secs) = @_;
    my $end = time + $secs;
    my $out = "";
    while (time < $end) {
        my $rout   = $rin;
        my $remain = $end - time;
        last if $remain <= 0;
        $remain = 0.05 if $remain > 0.05;
        my $n = select($rout, undef, undef, $remain);
        if ($n > 0) {
            my $buf = "";
            my $r = sysread($fh, $buf, 8192);
            $out .= $buf if $r;
        }
        return ($out, 1) if defined $want && $out =~ /$want/;
    }
    return ($out, 0);
}

for (1 .. 12) {
    syswrite($fh, "\x03");
    sleep 0.05;
}
my ($prompt) = read_until(qr/>>> \z/, 3);
print STDERR "PROMPT: ", (substr($prompt, -40) =~ s/[\r\n]+/ | /gr), "\n";

print "==== TRANSCRIPT ====\n";
for my $line (@lines) {
    syswrite($fh, $line . "\r");
    my ($out, $hit) = read_until(qr/(?:>>> |\.\.\. )\z/, 30);
    # A compound statement leaves the REPL on the "..." continuation prompt
    # until it gets a blank line.
    if ($out =~ /\.\.\. \z/) {
        syswrite($fh, "\r");
        my ($more, $hit2) = read_until(qr/>>> \z/, 30);
        $out .= $more;
        $hit = $hit2;
    }
    $out =~ s/\r//g;
    $out =~ s/\n?\.\.\. //g;
    $out =~ s/^\Q$line\E\n?//;    # drop the REPL's echo of what we just sent
    $out =~ s/\n?>>> \z//;
    printf "%-52s | %s\n", $line, ($out =~ s/\n/ ; /gr);
    unless ($hit) {
        print "*** no prompt after 30s, stopping ***\n";
        last;
    }
}
print "==== END ====\n";

restore();
my ($boot) = read_until(qr/adc live|fps /, 12);
$boot =~ s/\r//g;
print "==== AFTER RESET ====\n$boot\n==== END ====\n";
close $fh;

sub default_code {
    return <<'PY';
print("PING")
import sys
print("IMPL", sys.implementation)
import fft_q15
print("FFTOK", fft_q15.FFT(256).n())
PY
}
