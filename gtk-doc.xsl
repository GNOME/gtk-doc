<?xml version='1.0'?> <!--*- mode: xml -*-->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                version='1.0'
                xmlns="http://www.w3.org/TR/xhtml1/transitional"
                exclude-result-prefixes="#default">

  <!-- import the chunked XSL stylesheet -->
  <xsl:import href="http://docbook.sourceforge.net/release/xsl/current/html/chunk.xsl"/>
  <xsl:include href="devhelp.xsl"/>

  <!-- change some parameters -->
  <xsl:param name="toc.section.depth">1</xsl:param>

  <xsl:param name="default.encoding" select="UTF-8"/>
  <xsl:param name="chapter.autolabel" select="0"/>
  <xsl:param name="use.id.as.filename" select="'1'"/>
  <xsl:param name="html.ext" select="'.html'"/>
  <xsl:param name="refentry.generate.name" select="0"/>
  <xsl:param name="refentry.generate.title" select="1"/>

  <!-- display variablelists as tables -->
  <xsl:param name="variablelist.as.table" select="1"/>

  <!-- this gets set on the command line ... -->
  <xsl:param name="gtkdoc.bookname" select="''"/>

  <!-- ========================================================= -->
  <!-- template to create the index.sgml anchor index -->

  <xsl:template match="book|article">
    <xsl:apply-imports/>

    <!-- generate the index.sgml href index -->
    <xsl:call-template name="generate.index"/>
    <xsl:call-template name="generate.devhelp"/>
  </xsl:template>

  <xsl:template name="generate.index">
    <xsl:call-template name="write.text.chunk">
      <xsl:with-param name="filename" select="'index.sgml'"/>
      <xsl:with-param name="content">
        <!-- check all anchor and refentry elements -->
        <xsl:apply-templates select="//anchor|refentry"
                             mode="generate.index.mode"/>
      </xsl:with-param>
      <xsl:with-param name="encoding" select="'utf-8'"/>
    </xsl:call-template>
  </xsl:template>

  <xsl:template match="*" mode="generate.index.mode">
    <xsl:if test="not(@href)">
      <xsl:text>&lt;ANCHOR id=&quot;</xsl:text>
      <xsl:value-of select="@id"/>
      <xsl:text>&quot; href=&quot;</xsl:text>
      <xsl:if test="$gtkdoc.bookname">
        <xsl:value-of select="$gtkdoc.bookname"/>
        <xsl:text>/</xsl:text>
      </xsl:if>
      <xsl:call-template name="href.target"/>
      <xsl:text>&quot;&gt;
</xsl:text>
    </xsl:if>
  </xsl:template>

  <!-- ========================================================= -->
  <!-- template to output gtkdoclink elements for the unknown targets -->

  <xsl:template match="link">
    <xsl:choose>
      <xsl:when test="id(@linkend)">
        <xsl:apply-imports/>
      </xsl:when>
      <xsl:otherwise>
        <GTKDOCLINK HREF="{@linkend}">
          <xsl:apply-templates/>
        </GTKDOCLINK>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!-- ========================================================= -->
  <!-- Below are the visual portions of the stylesheet.  They provide
       the normal gtk-doc output style. -->

  <xsl:param name="shade.verbatim" select="0"/>
  <xsl:param name="refentry.separator" select="0"/>

  <xsl:template match="refsect2">
    <xsl:if test="preceding-sibling::refsect2">
      <hr/>
    </xsl:if>
    <xsl:apply-imports/>
  </xsl:template>

  <xsl:template name="user.head.content">
    <style>
      <xsl:text>
        .synopsis, .programlisting {
            background: #D6E8FF;
            padding: 4px;
        }
        .variablelist {
            background: #FFD0D0;
            padding: 4px;
        }
      </xsl:text>
    </style>
  </xsl:template>

  <xsl:template match="title" mode="book.titlepage.recto.mode">
    <table width="100%" border="0" bgcolor="#000000"
           cellpadding="1" cellspacing="0">
      <tr>
        <th align="center" valign="center">
          <p class="{name(.)}">
            <font color="#FFFFFF" size="7">
              <xsl:value-of select="."/>
            </font>
          </p>
        </th>
      </tr>
    </table>
  </xsl:template>

  <xsl:template name="header.navigation">
    <xsl:param name="prev" select="/foo"/>
    <xsl:param name="next" select="/foo"/>
    <xsl:variable name="home" select="/*[1]"/>
    <xsl:variable name="up" select="parent::*"/>

    <xsl:if test="$suppress.navigation = '0' and $home != .">
      <table bgcolor="#000000" width="100%" summary="Navigation header"
             cellpadding="1" cellspacing="0">
        <tr>
          <th colspan="4" align="center">
            <font color="#FFFFFF" size="5">
              <xsl:apply-templates select="$home" mode="object.title.markup"/>
            </font>
          </th>
        </tr>
        <tr>
          <td width="25%" bgcolor="#C00000" align="left">
            <xsl:if test="count($prev) > 0">
              <a accesskey="p">
                <xsl:attribute name="href">
                  <xsl:call-template name="href.target">
                    <xsl:with-param name="object" select="$prev"/>
                  </xsl:call-template>
                </xsl:attribute>
                <font color="#FFFFFF" size="3">
                  <b>
                    <xsl:text>&lt;&lt;&lt;&#160;</xsl:text>
                    <xsl:call-template name="gentext">
                      <xsl:with-param name="key">nav-prev</xsl:with-param>
                    </xsl:call-template>
                  </b>
                </font>
              </a>
            </xsl:if>
          </td>
          <td width="25%" bgcolor="#0000C0" align="center">
            <xsl:if test="$home != .">
              <a accesskey="h">
                <xsl:attribute name="href">
                  <xsl:call-template name="href.target">
                    <xsl:with-param name="object" select="$home"/>
                  </xsl:call-template>
                </xsl:attribute>
                <font color="#FFFFFF" size="3">
                  <b>
                    <xsl:call-template name="gentext">
                      <xsl:with-param name="key">nav-home</xsl:with-param>
                    </xsl:call-template>
                  </b>
                </font>
              </a>
            </xsl:if>
          </td>
          <td width="25%" bgcolor="#00C000" align="center">
            <xsl:if test="count($up) > 0 and $up != $home">
              <a accesskey="u">
                <xsl:attribute name="href">
                  <xsl:call-template name="href.target">
                    <xsl:with-param name="object" select="$up"/>
                  </xsl:call-template>
                </xsl:attribute>
                <font color="#FFFFFF" size="3">
                  <b>
                    <xsl:call-template name="gentext">
                      <xsl:with-param name="key">nav-up</xsl:with-param>
                    </xsl:call-template>
                  </b>
                </font>
              </a>
            </xsl:if>
          </td>
          <td width="25%" bgcolor="#C00000" align="right">
            <xsl:if test="count($next) > 0">
              <a accesskey="n">
                <xsl:attribute name="href">
                  <xsl:call-template name="href.target">
                    <xsl:with-param name="object" select="$next"/>
                  </xsl:call-template>
                </xsl:attribute>
                <font color="#FFFFFF" size="3">
                  <b>
                    <xsl:call-template name="gentext">
                      <xsl:with-param name="key">nav-next</xsl:with-param>
                    </xsl:call-template>
                    <xsl:text>&#160;&gt;&gt;&gt;</xsl:text>
                  </b>
                </font>
              </a>
            </xsl:if>
          </td>
        </tr>
      </table>
    </xsl:if>
  </xsl:template>

  <xsl:template name="footer.navigation">
    <xsl:param name="prev" select="/foo"/>
    <xsl:param name="next" select="/foo"/>
    <xsl:variable name="home" select="/*[1]"/>
    <xsl:variable name="up" select="parent::*"/>

    <xsl:if test="$suppress.navigation = '0'">
      <table bgcolor="#000000" width="100%" summary="Navigation footer"
             cellpadding="1" cellspacing="0">
        <tr>
          <td width="25%" bgcolor="#C00000" align="left">
            <xsl:if test="count($prev) > 0">
              <a accesskey="p">
                <xsl:attribute name="href">
                  <xsl:call-template name="href.target">
                    <xsl:with-param name="object" select="$prev"/>
                  </xsl:call-template>
                </xsl:attribute>
                <font color="#FFFFFF" size="3">
                  <b>
                    <xsl:text>&lt;&lt;&lt;&#160;</xsl:text>
                    <xsl:call-template name="gentext">
                      <xsl:with-param name="key">nav-prev</xsl:with-param>
                    </xsl:call-template>
                  </b>
                </font>
              </a>
            </xsl:if>
          </td>
          <td width="25%" bgcolor="#0000C0" align="center">
            <xsl:if test="$home != .">
              <a accesskey="h">
                <xsl:attribute name="href">
                  <xsl:call-template name="href.target">
                    <xsl:with-param name="object" select="$home"/>
                  </xsl:call-template>
                </xsl:attribute>
                <font color="#FFFFFF" size="3">
                  <b>
                    <xsl:call-template name="gentext">
                      <xsl:with-param name="key">nav-home</xsl:with-param>
                    </xsl:call-template>
                  </b>
                </font>
              </a>
            </xsl:if>
          </td>
          <td width="25%" bgcolor="#00C000" align="center">
            <xsl:if test="count($up) > 0 and $up != $home">
              <a accesskey="u">
                <xsl:attribute name="href">
                  <xsl:call-template name="href.target">
                    <xsl:with-param name="object" select="$up"/>
                  </xsl:call-template>
                </xsl:attribute>
                <font color="#FFFFFF" size="3">
                  <b>
                    <xsl:call-template name="gentext">
                      <xsl:with-param name="key">nav-up</xsl:with-param>
                    </xsl:call-template>
                  </b>
                </font>
              </a>
            </xsl:if>
          </td>
          <td width="25%" bgcolor="#C00000" align="right">
            <xsl:if test="count($next) > 0">
              <a accesskey="n">
                <xsl:attribute name="href">
                  <xsl:call-template name="href.target">
                    <xsl:with-param name="object" select="$next"/>
                  </xsl:call-template>
                </xsl:attribute>
                <font color="#FFFFFF" size="3">
                  <b>
                    <xsl:call-template name="gentext">
                      <xsl:with-param name="key">nav-next</xsl:with-param>
                    </xsl:call-template>
                    <xsl:text>&#160;&gt;&gt;&gt;</xsl:text>
                  </b>
                </font>
              </a>
            </xsl:if>
          </td>
        </tr>
        <tr>
          <td colspan="2" align="left">
            <xsl:if test="count($prev) > 0">
              <font color="#FFFFFF" size="3">
                <b>
                  <xsl:apply-templates select="$prev"
                                       mode="object.title.markup"/>
                </b>
              </font>
            </xsl:if>
          </td>
          <td colspan="2" align="right">
            <xsl:if test="count($next) > 0">
              <font color="#FFFFFF" size="3">
                <b>
                  <xsl:apply-templates select="$next"
                                       mode="object.title.markup"/>
                </b>
              </font>
            </xsl:if>
          </td>
        </tr>
      </table>
    </xsl:if>
  </xsl:template>

</xsl:stylesheet>
